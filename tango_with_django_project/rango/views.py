from django.shortcuts import render, redirect
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm, EditUserForm
from rango.bing_search import run_query
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.contrib.auth.models import User

# Create your views here.

def index(request):
    context_dict = {}

    most_liked_categories = Category.objects.order_by("-likes")[:5]
    context_dict['most_liked_categories'] = most_liked_categories

    most_viewed_categories = Category.objects.order_by("-views")[:5]
    context_dict['most_viewed_categories'] = most_viewed_categories

    visits = request.session.get("visits")
    if not visits:
        visits = 1

    reset_last_visit_time = False

    last_visit = request.session.get("last_visit")
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time).seconds > 0:
            visits = visits + 1
            reset_last_visit_time = True
    else:
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session["last_visit"] = str(datetime.now())
        request.session["visits"] = visits

    context_dict["visits"] = visits

    return render(request, 'rango/index.html', context_dict)


def about(request):
    visits = request.session.get("visits")
    if not visits:
        visits = 0

    return render(request, "rango/about.html", {"visits": visits})


def category(request, category_name_slug):

    context_dict = {}

    if request.method == 'POST':
        #User searching for more pages to add to Category, do search and return results
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)
            context_dict['result_list'] = result_list

    try:
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category'] = category
        context_dict['category_name'] = category.name
        context_dict['category_name_slug'] = category.slug

        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages

    except Category.DoesNotExist:
        pass

    return render(request, 'rango/category.html', context_dict)


def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)

        if form.is_valid():
            # Save the new category to the database.
            cat = form.save(commit=True)
            print cat, cat.slug

            # Now call the index() view.
            # The user will be shown the homepage.
            return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = CategoryForm()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render(request, "rango/add_category.html", {"form":form})


def add_page(request, category_name_slug):

    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat = None

    if request.method == "POST":
        form = PageForm(request.POST)

        if form.is_valid():
            if cat:
                # Save the new category to the database.
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()
                print page

                # probably better to use a redirect here.
                return category(request, category_name_slug)

            # Now call the index() view.
            # The user will be shown the homepage.
            return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = PageForm()

    context_dict = {"form": form, "category": cat, "category_name": cat.name}

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render(request, "rango/add_page.html", context_dict)


@login_required
def restricted(request):
    return render(request, "rango/restricted.html", {})


def search(request):
    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list})


def track_url(request):
    if request.method == 'GET' and 'page_id' in request.GET:
        page_id = request.GET['page_id']
        page = Page.objects.get(id=int(page_id))
        #print 'About to view page {0} which has been viewed {1} times already.'.format(page.title, page.views)
        page.views = page.views+1
        page.save()

        return redirect(page.url)
    else:
        return redirect("/rango/")


def register_profile(request, user_id):
    print "register_profile, user_id = ",user_id

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        profile_form = UserProfileForm(data=request.POST)

        if profile_form.is_valid():
            user = User.objects.get(id=int(user_id))

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print profile_form.errors

        return redirect("/rango/")

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        profile_form = UserProfileForm()
        return render(request, 'registration/profile_registration.html', {"profile_form":profile_form})

    # Render the template depending on the context.


def profile(request, user_id):
    editable = int(user_id) == request.user.id
    user = User.objects.get(id=int(user_id))
    profile = UserProfile.objects.get(user=user)

    if request.method == "POST":
        if editable:
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            user_form = EditUserForm(data=request.POST, instance=user)
            profile_form = UserProfileForm(data=request.POST, instance=profile)

            user_form.save()
            profile_form.save()

        else:
            print "Can't edit someone else's profile!"
            user_form = EditUserForm(instance=user)
            profile_form = UserProfileForm(instance=profile)

    else:
        user_form = EditUserForm(instance=user)
        profile_form = UserProfileForm(instance=profile)


    context_dict = {"user_form":user_form, "profile_form":profile_form, "editable":editable}

    return render(request, 'registration/profile.html', context_dict)


def profiles(request):
    profiles = UserProfile.objects.all()

    return render(request, 'registration/profiles.html', {"profiles":profiles})


from django.contrib.auth.decorators import login_required

@login_required
def like_category(request):

    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']

    likes = 0
    if cat_id:
        cat = Category.objects.get(id=int(cat_id))
        if cat:
            likes = cat.likes + 1
            cat.likes =  likes
            cat.save()

    return HttpResponse(likes)


def get_category_list(max_results=0, starts_with=''):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__istartswith=starts_with)
    else:
        cat_list = Category.objects.all()

    if max_results > 0:
            if len(cat_list) > max_results:
                    cat_list = cat_list[:max_results]

    return cat_list


def suggest_category(request):
    suggested = []

    if request.method == 'GET':
        starts_with = request.GET['suggestion']
        max_results = 8

        suggested = get_category_list(max_results, starts_with)

    return render(request, "rango/cats.html", {"cats": suggested})


@login_required
def auto_add_page(request):
    cat_id = None
    url = None
    title = None
    context_dict = {}

    if request.method == 'GET':
        cat_id = request.GET['category_id']
        url = request.GET['url']
        title = request.GET['title']

        if cat_id:
            cat = Category.objects.get(id=int(cat_id))
            p = Page.objects.get_or_create(category=cat, title=title, url=url)

            query_set = Page.objects.filter(category=cat)
            pages = query_set.order_by('-views')

            # Adds our results list to the template context under name pages.
            context_dict['pages'] = pages

    return render(request, 'rango/pages.html', context_dict)
