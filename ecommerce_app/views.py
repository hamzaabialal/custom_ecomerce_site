from django.views.generic.edit import FormView
from django.views.generic.detail import DetailView
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserTemplateForm
from .models import UserTemplate
import charset_normalizer  # Install with `pip install charset-normalizer`


def read_file(file):
    """
    Reads file content with automatic encoding detection.
    Uses charset_normalizer for encoding detection and fallback if needed.
    """
    raw_data = file.read()
    result = charset_normalizer.detect(raw_data)
    encoding = result['encoding'] or 'utf-8'  # Default to utf-8 if detection fails

    try:
        # Try to decode with detected encoding
        return raw_data.decode(encoding)
    except (UnicodeDecodeError, TypeError):
        # If the detected encoding doesn't work, fallback to a different encoding
        return raw_data.decode('ISO-8859-1', errors='ignore')


class UploadTemplateView(LoginRequiredMixin, FormView):
    template_name = 'upload_template.html'
    form_class = UserTemplateForm

    def form_valid(self, form):
        # Read file content
        html_file = self.request.FILES['html_file']
        css_file = self.request.FILES['css_file']
        js_file = self.request.FILES['js_file']

        try:
            html_content = read_file(html_file)
            css_content = read_file(css_file)
            js_content = read_file(js_file)

            # Save to the database
            user_template = UserTemplate.objects.create(
                user=self.request.user,
                html_content=html_content,
                css_content=css_content,
                js_content=js_content,
            )

            # Redirect to the template view with pk
            return redirect('view_template', pk=user_template.id)

        except UnicodeDecodeError as e:
            # Log error or notify user
            return HttpResponse(f"Error reading file: {str(e)}", status=400)


class ViewTemplateView(LoginRequiredMixin, DetailView):
    model = UserTemplate
    context_object_name = 'user_template'
    template_name = 'view_template.html'

    def get_queryset(self):
        # Restrict access to templates owned by the logged-in user
        return UserTemplate.objects.filter(user=self.request.user)

    def render_to_response(self, context, **response_kwargs):
        user_template = context['user_template']

        # Get the content from the database
        html_content = user_template.html_content
        css_content = user_template.css_content
        js_content = user_template.js_content

        # Inject CSS and JS content into the HTML
        html_content = f"""
        <html>
        <head>
            <style>{css_content}</style>
            <script>{js_content}</script>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """

        return HttpResponse(html_content)
