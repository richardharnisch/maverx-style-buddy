"""Pydantic model for a style guide definition."""

from pydantic import BaseModel


class Colors(BaseModel):
    primary: str = "#1F3864"
    secondary: str = "#2E75B6"
    accent: str = "#ED7D31"
    background: str = "#FFFFFF"
    text: str = "#212121"


class Fonts(BaseModel):
    heading: str = "Calibri"
    body: str = "Calibri"
    heading_size: int = 32
    body_size: int = 18


class SlideSize(BaseModel):
    width_emu: int = 9144000
    height_emu: int = 5143500


class Logo(BaseModel):
    path: str | None = None
    position: str = "bottom_right"


class LayoutConfig(BaseModel):
    title_top: float | None = None
    title_left: float | None = None
    body_top: float | None = None


class Layouts(BaseModel):
    title: LayoutConfig = LayoutConfig()
    content: LayoutConfig = LayoutConfig()


class TextArea(BaseModel):
    """A single editable text box extracted from a template slide."""
    role: str                    # title | subtitle | body | left_column | right_column | caption
    shape_name: str
    left: int
    top: int
    width: int
    height: int
    font_name: str | None = None
    font_size_pt: float | None = None
    bold: bool | None = None
    italic: bool | None = None
    underline: bool | None = None
    color: str | None = None       # explicit hex e.g. "#FFFFFF"; None means inherit from theme
    alignment: str | None = None   # "left" | "center" | "right" | "justify"
    # Styled auto-shape properties (only set when the shape is not a plain text box)
    shape_preset: str | None = None    # XML prst value, e.g. "roundRect", "ellipse", "rect"
    bg_color: str | None = None        # shape fill/background color hex
    corner_radius: float | None = None # 0.0–0.5; only relevant for roundRect


class ImageArea(BaseModel):
    """A picture/image shape on a template slide."""
    role: str                      # background | photo | icon | decoration
    shape_name: str
    left: int
    top: int
    width: int
    height: int
    image_key: str | None = None   # key in images/catalog.yaml for the default image


class DecorativeShape(BaseModel):
    """A non-text, non-image shape (rectangle, oval, line, freeform) that contributes to the visual design."""
    shape_name: str
    shape_type: str                # "auto_shape" | "line" | "freeform"
    shape_preset: str | None = None  # XML prst e.g. "rect", "roundRect", "ellipse", "line"
    left: int
    top: int
    width: int
    height: int
    fill_color: str | None = None  # solid fill hex
    border_color: str | None = None
    border_pt: float | None = None
    corner_radius: float | None = None  # 0.0–0.5 for roundRect


class SlideTemplate(BaseModel):
    """Describes one unique slide type extracted from a branded PPTX template."""
    key: str
    source_slide_index: int
    layout_name: str
    description: str
    text_areas: list[TextArea] = []
    image_areas: list[ImageArea] = []
    decorative_shapes: list[DecorativeShape] = []
    table_count: int = 0
    non_text_shapes: int = 0


class StyleGuide(BaseModel):
    name: str
    template_pptx: str | None = None
    layouts_dir: str | None = None   # relative path from project root, e.g. "style_guides/maverx"
    colors: Colors | None = None
    fonts: Fonts | None = None
    slide_size: SlideSize | None = None
    logo: Logo = Logo()
    layouts: Layouts = Layouts()
