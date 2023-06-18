from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.urls import reverse
from django.views.decorators.http import require_http_methods


from .models import User, AuctionListing, Bid, Comment, Watchlist, CurrentHighestBid
from .forms import CreateListingForm, CommentForm, BidForm


def index(request):
    all_listings = AuctionListing.objects.all()
    return render(request, "auctions/index.html", {"all_listings": all_listings})


def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
    else:
        return render(
            request,
            "auctions/login.html",
            {"message": "Invalid username and/or password."},
        )


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


@require_http_methods(["POST"])
def register(request):
    username = request.POST["username"]
    email = request.POST["email"]

    # Ensure password matches confirmation
    password = request.POST["password"]
    confirmation = request.POST["confirmation"]
    if password != confirmation:
        return render(
            request, "auctions/register.html", {"message": "Passwords must match."}
        )

    # Attempt to create new user
    try:
        user = User.objects.create_user(username, email, password)
        user.save()
    except IntegrityError:
        return render(
            request,
            "auctions/register.html",
            {"message": "Username already taken."},
        )
    login(request, user)

    return HttpResponseRedirect(reverse("index"))


@login_required
def create_listing(request):
    return render(
        request, "auctions\create_listing.html", {"form": CreateListingForm()}
    )


@require_http_methods(["POST"])
@login_required
def save_listing(request):
    listing_form = CreateListingForm(request.POST, request.FILES)
    
    if not listing_form.is_valid():
        return HttpResponseBadRequest
    
    new_listing = AuctionListing(
        title=listing_form.cleaned_data["title"],
        description=listing_form.cleaned_data["description"],
        photo=listing_form.cleaned_data["photo"],
        starting_bid=listing_form.cleaned_data["starting_bid"],
        owner=request.user,
        category=listing_form.cleaned_data["category"]
    )
    new_listing.save()
    
    return HttpResponseRedirect(reverse("index"))


def listing_view(request, listing_id, message=None):
    """
    Generates a listing page containing information about the listing
    and renders it
    Also there should be a comments/bids form somewhere
    """

    # Check if the user's watchlist contains current listing
    watchlist_ids = []
    if Watchlist.objects.filter(watchlist_owner=request.user).exists():
        for watchlist_listing in Watchlist.objects.filter(watchlist_owner=request.user):
            watchlist_ids.append(watchlist_listing.listing.id)
            
    current_listing = AuctionListing.objects.get(id=listing_id)
    
    in_watchlist = True if listing_id in watchlist_ids else False
    # Try to fetch current highest bid
    try:
        current_highest_bid_obj = CurrentHighestBid.objects.get(listing=current_listing)
        current_highest_bid = Bid.objects.get(listing=current_listing).bid_amount
    except CurrentHighestBid.DoesNotExist:
        current_highest_bid = None
    
    render_dict = {
        "bid": None,
        "listing": AuctionListing.objects.get(id=listing_id),
        "comment_form": CommentForm(),
        "bid_form": BidForm(),
        "comments": Comment.objects.filter(listing=listing_id),
        "in_watchlist": in_watchlist,
        "message": message,
    }
    
    # Bidding logic
    if request.method == "POST" and current_listing.is_closed == False:
        # Obtain bid amount from the form
        bid_form = BidForm(request.POST)
        bid_form.is_valid()

        bid_amount = bid_form.cleaned_data["bid"]
        listing = AuctionListing.objects.get(id=listing_id)

        # Obtain starting bid amount from the listing
        starting_bid = listing.starting_bid

        if bid_amount < starting_bid:
            render_dict["bid"] = current_listing.starting_bid if current_highest_bid is None else current_highest_bid
            render_dict["message"] = "The bid you have placed is lower than the starting bid"
            return render(
                request,
                "auctions\listing.html",
                render_dict,
            )

        if current_highest_bid is None or bid_amount > current_highest_bid:
            new_bid = Bid.objects.create(
                bid_amount=bid_amount,
                bidder=request.user,
                listing=AuctionListing.objects.get(id=listing_id),
            )
            try:
                current_highest_bid.bid = new_bid
                current_highest_bid.save()
            except AttributeError as e:
                new_current_highest_bid = CurrentHighestBid.objects.create(
                    listing=current_listing,
                    bid=new_bid
                )
            render_dict["bid"] = bid_amount
            return render(
                request,
                "auctions\listing.html",
                render_dict,
            )
        else:
            render_dict["bid"] = current_highest_bid
            render_dict["message"] = "The bid you have placed is lower than the current highest bid"
            return render(
                request,
                "auctions\listing.html",
                render_dict,
            )
    render_dict["bid"] = current_listing.starting_bid if current_highest_bid is None else current_highest_bid
    render_dict["message"] = message
    return render(
        request,
        "auctions\listing.html",
        render_dict,
    )


@require_http_methods(["POST"])
@login_required
def post_comment_view(request, listing_id):
    """
    View for processing posted comments
    Adds them to the database
    """
    comment_form = CommentForm(request.POST)
    comment_form.is_valid()
    new_comment = Comment(
        comment=comment_form.cleaned_data["comment"],
        author=request.user,
        listing=AuctionListing.objects.get(id=listing_id),
    )
    new_comment.save()

    return HttpResponseRedirect(reverse(viewname="listing", args=(listing_id,)))


@login_required
def watchlist_view(request):
    """
    View that handles watchlist logic
    Adding/removing listings from users watchlist
    """
    # Smells like a terrible hack, also kinda slow
    watchlist_listings_ids = []
    watchlist = None
    if Watchlist.objects.filter(watchlist_owner=request.user).exists():
        for watchlist_listing in Watchlist.objects.filter(watchlist_owner=request.user):
            watchlist_listings_ids.append(watchlist_listing.listing.id)
        watchlist = AuctionListing.objects.filter(id__in=watchlist_listings_ids)

    return render(
        request,
        "auctions\watchlist.html",
        {"watchlist": watchlist},
    )


@require_http_methods(["POST"])
@login_required
def add_to_watchlist(request):
    """
    View for adding items to watchlist
    I didn't use a django form in this one and I regret it immensely

    Args:
        request

    Returns:
        redirect to watchlist
    """
    new_watchlist_item = Watchlist(
        watchlist_owner=request.user,
        listing=AuctionListing.objects.get(id=request.POST["listing_id"]),
    )
    new_watchlist_item.save()
    return HttpResponseRedirect(
        reverse(viewname="listing", args=(request.POST["listing_id"],))
    )


@require_http_methods(["POST"])
@login_required
def remove_from_watchlist_view(request):
    """
    Removes an item from users watchlist
    Deletes the record in the Watchlist model
    """

    auction_listing = AuctionListing.objects.get(id=request.POST["listing_id"])
    Watchlist.objects.get(listing=auction_listing).delete()
    return HttpResponseRedirect(reverse("watchlist"))


@require_http_methods(["POST"])
@login_required
def close_listing_view(request, listing_id):
    """
    Closes the listing, prevents further bids
    """
    listing = AuctionListing.objects.get(id=listing_id)
    if request.user == listing.owner:
        listing.is_closed = True
        listing.save()
    
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))