# I want to
## create a new webpage 
1. Go into your apps folder (likely /fancybar) 
2. Open urls.py
3. Find the ```urlpatterns``` list
4. Add an entry like this url(a, b, name='c')

   where
   
   4.1 a is a regex of the url you want to link to the new page
   If you want to create website.com/upload, write ```r'^upload$'```
   Note that ```^``` denotes the start of a string and ```$``` denotes the end of a string
   
   4.2 b is a view, as defined in view.py later on in step 
   Take the name of that class and add ```.as_view()```, like this:
   ```Mysite.as_view()```
   
   4.3 c is a name for reference. Pick the same as the classname, but in lower case
   
   Example:
   ```url(r'^$', Fancybar.as_view(), name='fancybar')),```
5. Add a new class in views.py
   In most cases, your class should inherit from TemplateView
6. Implement basic get and post methods that simply return a render of your template
   Example:
   ```python
   class Fancybar(TemplateView):
        template_name = 'mytemplate.html'
        def get(self, request):
                return render(request, self.template_name)


        def post(self, request):
                return render(request, self.template_name)
   ```

7. Make sure the template file exists in templates/mytemplate.html, if not continue
## Create a new template
TODO
## style my page with css
### Really?
1. Do you just need bootstrap, font awesome, etc? Check if its not already imported by a higher template.
2. cd into /fancybar/static/fancybar/css/
3. Check existing files: Does one of them contain what you want?
4. If so, goto 6, else continue
### Create file
5. Create one or more new css files with a single purpose each
### Link css to html
6. cd back into base (the folder where manage.py is located)
7. Run `./manage.py collectstatic` (or `python manage.py collectstatic` in lesser OSes)
8. Type "yes"
9. cd into /fancybar/tempates
10. Ensure the top of the file contains `{% load static %}`
11. In the html header, write 
```html
<link href="{% static 'fancybar/css/[your_file].css' %}" rel="stylesheet">
```
