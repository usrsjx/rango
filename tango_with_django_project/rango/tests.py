from django.test import TestCase
from rango.models import Category
from django.core.urlresolvers import reverse

class CategoryMethodTests(TestCase):

    def test_views_overridden_to_zero_if_negative_passed(self):
        cat = Category(name="test cat", views=-1, likes=0)
        cat.save()
        self.assertTrue(cat.views >= 0)


    def test_that_slug_created_correctly_from_name(self):
        cat = Category(name="A Test Category")
        cat.save()
        self.assertEqual(cat.slug, "a-test-category")


class IndexViewTests(TestCase):

    def test_that_no_categories_message_displayed_when_no_categories_present(self):
        response = self.client.get(reverse("index"))
        # print response
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There are no categories present.")
        self.assertQuerysetEqual(response.context['most_liked_categories'], [])
        self.assertQuerysetEqual(response.context['most_viewed_categories'], [])


    def test_index_view_with_categories(self):
        """
        If no questions exist, an appropriate message should be displayed.
        """

        add_cat('test',1,1)
        add_cat('temp',1,1)
        add_cat('tmp',1,1)
        add_cat('tmp test temp',1,1)

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "tmp test temp")

        self.assertEqual(len(response.context['most_liked_categories']) , 4)
        self.assertEqual(len(response.context['most_viewed_categories']) , 4)


def add_cat(name, views, likes):
    c = Category.objects.get_or_create(name=name)[0]
    c.views = views
    c.likes = likes
    c.save()
    return c