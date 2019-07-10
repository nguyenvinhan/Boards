from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.db.models import Count
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, ListView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Board, Topic, Post
from .forms import NewTopicForm, PostForm


class BoardListView(ListView):
    model = Board
    context_object_name = 'boards'
    template_name = 'home.html'

class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'topics.html'
    paginate_by = 10
    
    def get_context_data(self, **kwargs):
        kwargs['board'] = self.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('board_id'))
        queryset = self.board.topics.order_by('-last_updated').annotate(
        		   replies=Count('posts') - 1)
        return queryset


@login_required
def new_topic(request,board_id):
	board = get_object_or_404(Board, pk = board_id)
	if request.method == 'POST':
		# subject = request.POST['subject']
		# message = request.POST['message']
		# user = User.objects.first() #TODO: get the currently logged in user
		# topic = Topic.objects.create(subject = subject, board = board, starter = user)
		# post = Post.objects.create(message = message, topic = topic, created_by = user)
		form = NewTopicForm(request.POST)
		if form.is_valid():
			topic = form.save(commit=False)
			topic.board = board
			topic.starter = request.user
			topic.save()

			post = Post.objects.create(
				message = form.cleaned_data.get('message'),
				topic = topic,
				created_by = request.user
				)
			# return redirect('topic_posts', pk = board_id, topic_id = topic.pk)  # return redirect('board_topics',board.id)
			return redirect('board_topics',board.id)
	else:
		form = NewTopicForm(None, {})
	return render(request,'new_topic.html', {'board': board, 'form': form})


class PostListView(ListView):
	model = Post
	context_object_name = 'posts'
	template_name = 'topic_posts.html'
	paginate_by = 2

	def get_context_data(self, **kwargs):
		self.topic.views += 1
		self.topic.save()
		kwargs['topic'] = self.topic
		return super().get_context_data(**kwargs)
	
	def get_queryset(self):
		self.topic = get_object_or_404(Topic, board__pk = self.kwargs.get('board_id'),
    	pk=self.kwargs.get('topic_id'))
		queryset = self.topic.posts.order_by('created_at')
		return queryset

@login_required
def reply_topic(request, board_id,topic_id):
    topic = get_object_or_404(Topic, board__id = board_id, pk = topic_id)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()

            topic.last_updated = timezone.now()
            topic.save() 
            return redirect('topic_posts', board_id = board_id, topic_id = topic_id)
    else:
        form = PostForm()
    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})

@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message', )
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_id'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', board_id = post.topic.board.pk, topic_id = post.topic.pk)