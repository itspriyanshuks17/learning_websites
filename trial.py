import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from plyer import filechooser
from PIL import Image as PILImage, ImageEnhance, ImageOps
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

class DocScannerApp(App):
    def build(self):
        self.raw_image_paths = []
        self.current_filter = "ORIGINAL"
        
        # Main Layout
        root = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Image Preview
        self.preview_image = Image(source='', allow_stretch=True, keep_ratio=True)
        root.add_widget(self.preview_image)
        
        # Filter Buttons Row
        filter_scroll = ScrollView(size_hint=(1, 0.15))
        filter_layout = BoxLayout(orientation='horizontal', size_hint_x=None, spacing=5)
        filter_layout.bind(minimum_width=filter_layout.setter('width'))
        
        filters = ["ORIGINAL", "GRAYSCALE", "BLACK_WHITE", "MAGIC_COLOR"]
        for f in filters:
            btn = Button(text=f, size_hint_x=None, width=120)
            btn.bind(on_release=lambda instance, filter_name=f: self.apply_filter(filter_name))
            filter_layout.add_widget(btn)
            
        filter_scroll.add_widget(filter_layout)
        root.add_widget(filter_scroll)
        
        # Main Action Buttons
        btn_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.15), spacing=10)
        
        select_btn = Button(text="Select Images")
        select_btn.bind(on_release=self.select_images)
        
        export_btn = Button(text="Export PDF", background_color=(0, 0.7, 0.3, 1))
        export_btn.bind(on_release=self.export_pdf)
        
        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(export_btn)
        
        root.add_widget(btn_layout)
        return root

    def select_images(self, instance):
        filechooser.open_file(multiple=True, on_selection=self.on_files_selected)

    def on_files_selected(self, selection):
        if selection:
            self.raw_image_paths = selection
            self.update_preview()

    def apply_filter(self, filter_name):
        self.current_filter = filter_name
        self.update_preview()

    def process_pil_image(self, pil_img):
        if self.current_filter == "GRAYSCALE":
            return ImageOps.grayscale(pil_img).convert("RGB")
        elif self.current_filter == "BLACK_WHITE":
            gray = ImageOps.grayscale(pil_img)
            return gray.point(lambda p: 255 if p > 128 else 0).convert("RGB")
        elif self.current_filter == "MAGIC_COLOR":
            enhancer = ImageEnhance.Color(pil_img)
            return enhancer.enhance(1.5)
        return pil_img

    def update_preview(self):
        if not self.raw_image_paths:
            return
            
        temp_preview = os.path.join(self.user_data_dir, "temp_preview.jpg")
        img = PILImage.open(self.raw_image_paths[0])
        processed = self.process_pil_image(img)
        processed.save(temp_preview)
        
        self.preview_image.source = temp_preview
        self.preview_image.reload()

    def export_pdf(self, instance):
        if not self.raw_image_paths:
            return

        pdf_path = os.path.join(self.user_data_dir, "MergedDocument.pdf")
        c = canvas.Canvas(pdf_path, pagesize=A4)
        a4_width, a4_height = A4

        for idx, path in enumerate(self.raw_image_paths):
            img = PILImage.open(path)
            processed = self.process_pil_image(img)
            
            temp_path = os.path.join(self.user_data_dir, f"temp_{idx}.jpg")
            processed.save(temp_path)

            c.drawImage(temp_path, 0, 0, width=a4_width, height=a4_height)
            c.showPage()

        c.save()
        print(f"PDF successfully exported to: {pdf_path}")

if __name__ == '__main__':
    DocScannerApp().run()
