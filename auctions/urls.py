from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create_listing/", views.create_listing, name="create_listing"),
    path("save_listing/", views.save_listing, name="save_listing"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("add_to_watchlist/", views.add_to_watchlist, name="add to watchlist"),
    path("watchlist/", views.watchlist_view, name="watchlist"),
    path(
        "remove_from_watchlist/",
        views.remove_from_watchlist_view,
        name="remove_from_watchlist",
    ),
    path("listings/<int:listing_id>/", views.listing_view, name="listing"),
    path(
        "listings/<int:listing_id>/post_comment",
        views.post_comment_view,
        name="post_comment",
    ),
    path("listings/<int:listing_id>/", views.close_listing_view, name="close listing")
]
