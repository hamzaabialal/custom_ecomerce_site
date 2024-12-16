from django import forms

class UserTemplateForm(forms.Form):
    html_file = forms.FileField(required=True, label="HTML File")
    css_file = forms.FileField(required=True, label="CSS File")
    js_file = forms.FileField(required=True, label="JavaScript File")

    def clean_html_file(self):
        file = self.cleaned_data['html_file']
        if not file.name.endswith('.html'):
            raise forms.ValidationError("Please upload a valid HTML file.")
        return file

    def clean_css_file(self):
        file = self.cleaned_data['css_file']
        if not file.name.endswith('.css'):
            raise forms.ValidationError("Please upload a valid CSS file.")
        return file

    def clean_js_file(self):
        file = self.cleaned_data['js_file']
        if not file.name.endswith('.js'):
            raise forms.ValidationError("Please upload a valid JavaScript file.")
        return file
