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
  
6.1. *UPDATE:* While that still works, if you just want to render a simple html file, it is simpler to extend `GenericTemplate` like this:
   ```python
   class Fancybar(GenericTemplate):
        template_name = 'mytemplate.html'
   ```

7. Make sure the template file exists in templates/mytemplate.html, if not continue
## Create a new template
1. cd into cd into /fancybar/templates
2. Find a template you want to extend from.
   If you just want an empty page (but with configurations), extend from `base.html`.
   If you want a progress-navigation-bar, extend from `progbase.html`.
   You can also extend from any other file, but make sure to only use blocks that are empty in the parent.
   It should be easiest to copy and modify `template.html`, which extends progbase.
3. Ensure that your file starts with the lines `{%extends '[parent].html' %}` and `{% load static %}`
4. Change the title in the title block to something appropriate
5. If you need to load external css (or want to use djangos templating language within your css), place the code in the style block. This code is placed in the head, so if you write css, remember to enclose it in `<style>` tags.
6. Should you want to place code at the very top, before the navbar, you can do so in `prebody`.
7. Copy the content of the template.html files navbaritems block and change which item has the `active` class. I know, this could be solved more elegantly, but its the 1st sprint so plz no buly yet.
8. Put whatever body code you want in the body block
9. Similar to the style block, you can also add scripts to be loaded after the body (for a faster page display). If you really cant use static js and must hard code js or ts into your template, remember to enclose the code in `<script>` tags.
## style my page with css
### Really?
1. Do you just need bootstrap, font awesome, etc? Check if its not already imported by a higher template.
2. cd into /fancybar/static/fancybar/css/. Make sure you are in fancybars static folder, not in the one of equestria (*/equestria/static/fancybar/css is the wrong path*)
3. Check existing files: Does one of them contain what you want?
4. If so, goto 6, else continue
### Create file
5. Create one or more new css files with a single purpose each
### Link css to html
6. cd back into base (the folder where manage.py is located)
7. Run `./manage.py collectstatic` (or `python manage.py collectstatic` in lesser OSes) (although the server should pick that up by itself, so you should be fine without)
8. Type "yes"
9. cd into /fancybar/templates
10. Ensure the top of the file contains `{% load static %}`
11. In the html header, write 
```html
<link href="{% static 'fancybar/css/[your_file].css' %}" rel="stylesheet">
```
