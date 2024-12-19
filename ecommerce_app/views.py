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
import zipfile
import os
from django.core.files.storage import FileSystemStorage

import zipfile
import os
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from .models import UserTemplate

class UploadTemplateView(LoginRequiredMixin, FormView):
    template_name = 'upload_template.html'
    form_class = UserTemplateForm

    def form_valid(self, form):
        html_file = self.request.FILES['html_file']
        css_file = self.request.FILES['css_file']
        js_file = self.request.FILES['js_file']
        images_zip = form.cleaned_data.get('images_zip')

        try:
            html_content = read_file(html_file)
            css_content = read_file(css_file)
            js_content = read_file(js_file)

            # Save files to the database
            user_template = UserTemplate.objects.create(
                user=self.request.user,
                html_content=html_content,
                css_content=css_content,
                js_content=js_content,
            )

            # Handle image upload if ZIP file is provided
            if images_zip:
                # Create a directory to store images
                image_dir = os.path.join('media', 'user_images', str(user_template.id))
                os.makedirs(image_dir, exist_ok=True)

                # Extract images from ZIP file
                with zipfile.ZipFile(images_zip, 'r') as zip_ref:
                    zip_ref.extractall(image_dir)

                # Store the image directory in the user template model if needed
                user_template.image_dir = image_dir
                user_template.save()

            return redirect('view_template', pk=user_template.id)

        except UnicodeDecodeError as e:
            return HttpResponse(f"Error reading file: {str(e)}", status=400)



from django.http import HttpResponse
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

class ViewTemplateView(LoginRequiredMixin, DetailView):
    model = UserTemplate
    context_object_name = 'user_template'
    template_name = 'view_template.html'

    def render_to_response(self, context, **response_kwargs):
        user_template = context['user_template']

        # Retrieve the content from the database
        html_content = user_template.html_content
        css_content = user_template.css_content
        js_content = user_template.js_content

        # Modify HTML content to use correct image paths
        image_dir = user_template.image_dir
        if image_dir:
            # Replace relative image paths in the HTML content to use the correct media path
            html_content = html_content.replace('src="/', f'src="/media/user_images/{user_template.id}/images/')

            # For absolute or other relative paths, replace them accordingly
            # This will avoid appending `/media/user_images/{user_template.id}/` twice


        # Construct the complete HTML with embedded CSS and JavaScript
        full_html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>User Template</title>
            <style>{css_content}</style>
            <script>
                {js_content}
            </script>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """

        return HttpResponse(full_html_content)


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Cart

@csrf_exempt
def add_to_cart(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            product_name = data.get("product_name")
            product_price = data.get("product_price")
            quantity = data.get("quantity", 1)

            # Ensure the user is authenticated
            if not request.user.is_authenticated:
                return JsonResponse({"error": "User not authenticated."}, status=403)

            cart_item, created = Cart.objects.get_or_create(
                user=request.user,
                product_name=product_name,
                defaults={"product_price": product_price, "quantity": quantity},
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            return JsonResponse({"message": "Product added to cart successfully!"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)

