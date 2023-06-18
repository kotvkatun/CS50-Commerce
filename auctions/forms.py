from django import forms


class CreateListingForm(forms.Form):
    title = forms.CharField(max_length=30, label="Title:")
    description = forms.CharField(
        max_length=300, label="Description:", widget=forms.Textarea
    )
    photo = forms.URLField(label="Link a photo:", required=False)
    starting_bid = forms.DecimalField(
        max_digits=15, decimal_places=2, label="Starting bid:"
    )
    category = forms.ChoiceField(widget=forms.Select())


class CommentForm(forms.Form):
    comment = forms.CharField(
        max_length=400, label="Type your comment:", widget=forms.Textarea
    )


class BidForm(forms.Form):
    bid = forms.DecimalField(label="Place your bid:", max_digits=15, decimal_places=2)
