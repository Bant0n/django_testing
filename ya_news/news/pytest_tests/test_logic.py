import pytest
from news.models import Comment
from django.urls import reverse
from news.forms import WARNING, BAD_WORDS
from pytest_django.asserts import assertFormError
from news.forms import CommentForm
from random import choice


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, form_data):
    comments_count_before = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    client.post(url, form_data)
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before


@pytest.mark.django_db
def test_user_can_create_comment(author_client, news, form_data):
    url = reverse('news:detail', args=(news.id,))
    author_client.post(url, form_data)
    comments_count = Comment.objects.count()
    comments_obj = Comment.objects.get()
    assert comments_obj.text == form_data['text']
    assert comments_obj.author == form_data['author']
    assert comments_count == 1


@pytest.mark.django_db
def test_user_cant_create_bad_words(author_client, news):
    one_bad_word = choice(BAD_WORDS)
    bad_words = {'text': f'Какой-то текст, {one_bad_word}, еще текст'}
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, bad_words)
    assertFormError(
        response=response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    author_client.post(url)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_reader_can_delete_comment(client, comment):
    url = reverse('news:delete', args=(comment.id,))
    client.post(url)
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_author_can_edit_comment(comment, author_client):
    form_data = {'text': 'text'}
    url = reverse('news:edit', args=(comment.id,))
    author_client.post(url, form_data)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


@pytest.mark.django_db
def test_user_cant_edit_comment(comment, client):
    form_data = {'text': 'text'}
    url = reverse('news:edit', args=(comment.id,))
    client.post(url, form_data)
    comment.refresh_from_db()
    assert comment.text != form_data['text']
