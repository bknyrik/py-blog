from django.http import HttpRequest, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic


from .models import Post, Commentary
from .forms import CommentaryForm


class PostListView(generic.ListView):
    model = Post
    queryset = Post.objects.prefetch_related("owner").order_by("-created_time")
    paginate_by = 5
    template_name = "blog/index.html"


class PostDetailView(generic.DetailView):
    model = Post

    def post(self, request: HttpRequest, *args, **kwargs):
        self.object = self.get_object()
        form = CommentaryForm(request.POST)
        if form.is_valid() and request.user.is_authenticated:
            new_commentary = form.save(commit=False)
            new_commentary.post = self.object
            new_commentary.user = request.user
            new_commentary.save()

        return redirect(request.path)

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["form"] = CommentaryForm()
        context["form"].full_clean()

        if self.request.user.is_anonymous:
            context["form"].fields["content"].disabled = True

        context["user"] = self.request.user
        return context
