import streamlit as st
from io import BytesIO
import base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def create_download_link_pdf(pdf_data, download_filename):
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{download_filename}">Download PDF</a>'
    return href

def get_file_language(file_name: str) -> str:
    """Map filename or extension to Streamlit syntax highlighting language."""
    name_lower = file_name.lower()

    special_files = {
        "dockerfile": "dockerfile",
        "docker-compose.yml": "dockerfile",
        "docker-compose.yaml": "dockerfile",
        "makefile": "makefile",
        "gnumakefile": "makefile",
        "cmakelists.txt": "cmake",
    }
    if name_lower in special_files:
        return special_files[name_lower]

    ext = name_lower.split(".")[-1] if "." in name_lower else ""
    
    lang_map = {
        # Systems & Low-Level
        "c": "c", "h": "c",
        "cpp": "cpp", "cc": "cpp", "cxx": "cpp", "hpp": "cpp", "hxx": "cpp",
        "rs": "rust", "go": "go", "zig": "zig", "odin": "odin",
        "v": "v", "nim": "nim", "crystal": "crystal",
        
        # Assembly
        "asm": "asm", "s": "asm", "S": "asm", "nasm": "nasm",
        
        # Fortran & Scientific
        "f": "fortran", "f90": "fortran", "f95": "fortran",
        "f03": "fortran", "f08": "fortran", "for": "fortran", "f77": "fortran",
        
        # Functional & Lisp
        "lisp": "lisp", "cl": "lisp", "el": "elisp", "scm": "scheme", "rkt": "racket",
        "hs": "haskell", "lhs": "haskell",
        "ml": "ocaml", "mli": "ocaml",
        "fs": "fsharp", "fsx": "fsharp", "fsi": "fsharp",
        "erl": "erlang", "hrl": "erlang",
        "ex": "elixir", "exs": "elixir",
        
        # Modern & Popular
        "py": "python", "pyx": "python", "pyi": "python",
        "js": "javascript", "jsx": "jsx", "mjs": "javascript", "cjs": "javascript",
        "ts": "typescript", "tsx": "tsx",
        "java": "java",
        "kt": "kotlin", "kts": "kotlin",
        "scala": "scala", "sc": "scala",
        "cs": "csharp",
        "rb": "ruby",
        "php": "php",
        "swift": "swift",
        "dart": "dart",
        "lua": "lua",
        "jl": "julia",
        "r": "r", "rmd": "r",
        
        # Web & Markup
        "html": "html", "htm": "html",
        "htmx": "html",
        "css": "css", "scss": "scss", "sass": "sass", "less": "less",
        "md": "markdown", "markdown": "markdown",
        "rst": "rst", "adoc": "asciidoc",
        
        # Data & Config
        "json": "json", "yaml": "yaml", "yml": "yaml", "toml": "toml",
        "xml": "xml", "ini": "ini", "cfg": "ini", "conf": "ini",
        "properties": "properties", "env": "bash",
        
        # Database & Query
        "sql": "sql", "graphql": "graphql", "gql": "graphql",
        
        # Scripting & Shell
        "sh": "bash", "bash": "bash", "zsh": "bash", "fish": "fish",
        "ps1": "powershell", "psm1": "powershell",
        "bat": "batch", "cmd": "batch",
        "pl": "perl", "pm": "perl",
        
        # Others
        "matlab": "matlab", "m": "matlab",
        "prolog": "prolog", "sol": "solidity",
        "cu": "cuda", "cuh": "cuda",
        "cmake": "cmake", "proto": "protobuf",
        "txt": "text", "log": "text", "k": "text",
    }
    
    return lang_map.get(ext, "text")


# ====================== NEW: Categorized Languages ======================
LANGUAGE_CATEGORIES = {
    "Systems & Low-Level": ["c", "cpp", "rust", "go", "zig", "odin", "v", "nim", "crystal"],
    "Assembly": ["asm", "nasm"],
    "Fortran & Scientific": ["fortran"],
    "Functional & Lisp": ["lisp", "elisp", "scheme", "racket", "haskell", "ocaml", "fsharp", "erlang", "elixir"],
    "Modern & Popular": ["python", "javascript", "jsx", "typescript", "tsx", "java", "kotlin", "scala", "csharp", "ruby", "php", "swift", "dart", "lua", "julia", "r"],
    "Web & Markup": ["html", "css", "scss", "sass", "less", "markdown", "rst", "asciidoc"],
    "Data & Config": ["json", "yaml", "toml", "xml", "ini", "properties", "bash"],
    "Database & Query": ["sql", "graphql"],
    "Scripting & Shell": ["bash", "fish", "powershell", "batch", "perl"],
    "Others": ["matlab", "prolog", "solidity", "cuda", "cmake", "protobuf", "text", "dockerfile", "makefile"]
}

def get_category_for_lang(lang: str) -> str:
    for category, langs in LANGUAGE_CATEGORIES.items():
        if lang in langs:
            return category
    return list(LANGUAGE_CATEGORIES.keys())[0]
# ======================================================================


# Initialize session states
if 'task_list' not in st.session_state:
    st.session_state.task_list = []
if 'file_dict' not in st.session_state:
    st.session_state.file_dict = {}
if 'version_info' not in st.session_state:
    st.session_state.version_info = {}

st.title("Codebase Documentation Generator")

# Version Input
st.header("Version Information")
col1, col2 = st.columns(2)
with col1:
    app_version = st.text_input("App Version:")
with col2:
    interpreter_version = st.text_input("Interpreter Version:", placeholder="e.g., Python 3.12")

if st.button("Save Version Information"):
    if app_version and app_version not in st.session_state.task_list:
        st.session_state.task_list.append(app_version)
        st.session_state.version_info[app_version] = {
            'app_version': app_version,
            'interpreter_version': interpreter_version
        }

# File Upload
st.header("Upload Code Files")

supported_types = [...]  # (keep your full list)

uploaded_files = st.file_uploader(
    "Upload code files — supports 100+ languages including .md, HTMX, Rust, Go, Julia, Zig, etc.",
    accept_multiple_files=True,
    type=supported_types
)

if uploaded_files and app_version:
    if app_version not in st.session_state.file_dict:
        st.session_state.file_dict[app_version] = {}
    
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        try:
            file_content = uploaded_file.read().decode('utf-8')
        except UnicodeDecodeError:
            file_content = "Binary or non-UTF-8 content - cannot display"
        
        st.session_state.file_dict[app_version][file_name] = file_content

# ====================== IMPROVED PREVIEW SECTION ======================
st.header("Codebase Preview")

if app_version in st.session_state.file_dict:
    for file_name, file_content in st.session_state.file_dict[app_version].items():
        with st.expander(f"File: {file_name}"):
            detected_language = get_file_language(file_name)
            st.markdown(f"**Auto-detected:** `{detected_language}`")

            # === CATEGORIZED DROPDOWNS ===
            col1, col2 = st.columns(2)

            with col1:
                category_list = list(LANGUAGE_CATEGORIES.keys())
                default_category = get_category_for_lang(detected_language)
                cat_index = category_list.index(default_category) if default_category in category_list else 0

                selected_category = st.selectbox(
                    "Category",
                    category_list,
                    index=cat_index,
                    key=f"cat_{app_version}_{file_name}"
                )

            with col2:
                lang_list = LANGUAGE_CATEGORIES[selected_category]
                try:
                    lang_index = lang_list.index(detected_language)
                except ValueError:
                    lang_index = 0

                selected_language = st.selectbox(
                    "Language (syntax highlighting)",
                    lang_list,
                    index=lang_index,
                    key=f"lang_{app_version}_{file_name}"
                )

            # Display code with chosen language
            st.code(file_content, language=selected_language)

            if selected_language != detected_language:
                st.caption("✅ Using manually selected language")
# ======================================================================

# PDF Generation (unchanged)
if st.button("Generate and Download PDF"):
    if app_version and app_version in st.session_state.file_dict:
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, leftMargin=36, rightMargin=36)
        styles = getSampleStyleSheet()
        pdf_elements = []

        pdf_elements.append(Paragraph(f"App Version: {app_version}", styles['Heading1']))
        if app_version in st.session_state.version_info:
            interpreter_ver = st.session_state.version_info[app_version]['interpreter_version']
            pdf_elements.append(Paragraph(f"Interpreter Version: {interpreter_ver}", styles['Normal']))
            pdf_elements.append(Spacer(1, 10))

        pdf_elements.append(Paragraph("Codebase Files:", styles['Heading2']))
        for file_name, file_content in st.session_state.file_dict[app_version].items():
            pdf_elements.append(Paragraph(f"File: {file_name}", styles['Heading3']))
            code_style = ParagraphStyle('CodeStyle', fontName='Courier', fontSize=8,
                                        leftIndent=10, rightIndent=10, leading=8, wordWrap='CJK')
            pdf_elements.append(Preformatted(file_content, code_style, maxLineLength=65))
            pdf_elements.append(Spacer(1, 10))

        doc.build(pdf_elements)
        pdf_buffer.seek(0)
        pdf_data = pdf_buffer.read()
        st.markdown(create_download_link_pdf(pdf_data, f"codebase_{app_version}.pdf"), unsafe_allow_html=True)
    else:
        st.warning("Please upload files and specify an app version before generating PDF.")

# Saved versions
st.write("## Saved Versions")
for version in st.session_state.task_list:
    st.write(f"### App Version: {version}")
    if version in st.session_state.version_info:
        st.write(f"**Interpreter Version:** {st.session_state.version_info[version]['interpreter_version']}")
    st.write(f"Number of files: {len(st.session_state.file_dict.get(version, {}))}")
