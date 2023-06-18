from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(max_length=15, name="username", unique=True)
    email = models.EmailField(max_length=20, name="email")
    password = models.CharField(max_length=20, name="password")

    def __str__(self):
        return f"User: {self.username}, Email: {self.email}"


class AuctionListing(models.Model):
    title = models.CharField(max_length=25, name="title")
    description = models.TextField(name="description")
    starting_bid = models.DecimalField(
        name="starting_bid", max_digits=15, decimal_places=2
    )
    photo = models.URLField(name="photo")
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_closed = models.BooleanField(name="is_closed", default=False)
    category = models.CharField(max_length=30, name="category", default="Goods")
    
    def __str__(self):
        return f"Title: {self.title}"


class Bid(models.Model):
    bid_amount = models.DecimalField(name="bid_amount", max_digits=15, decimal_places=2)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)

    def __str__(self):
        return f"Bid {self.bid_amount}"


class CurrentHighestBid(models.Model):
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE)

    def __str__(self):
        return f"Highest bid {self.bid} for {self.listing}"


class Comment(models.Model):
    comment = models.TextField(name="comment", max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.comment}"


class Watchlist(models.Model):
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    watchlist_owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Watchlist for user {User.objects.get(id=watchlist_owner)}"


