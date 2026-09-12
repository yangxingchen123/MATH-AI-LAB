"""用代码打包最小 EPUB，避免提交二进制书。"""
from __future__ import annotations

import base64
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile, ZipInfo

# 1×1 PNG
MIN_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)

_CONTAINER = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""

_OPF = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>Minimal Book</dc:title>
    <dc:creator>Test Author</dc:creator>
    <dc:language>zh</dc:language>
    <dc:identifier id="BookId">urn:test:minimal</dc:identifier>
  </metadata>
  <manifest>
    <item id="ch1" href="ch1.xhtml" media-type="application/xhtml+xml"/>
    <item id="ch2" href="ch2.xhtml" media-type="application/xhtml+xml"/>
    <item id="img1" href="images/cover.png" media-type="image/png"/>
  </manifest>
  <spine>
    <itemref idref="ch1"/>
    <itemref idref="ch2"/>
  </spine>
</package>
"""

_CH1 = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<body>
<h1>Chapter One</h1>
<p>Hello <a href="ch2.xhtml#sec">next</a>.</p>
<p><img src="images/cover.png" alt="cover"/></p>
<table>
<tr><th>A</th><th>B</th></tr>
<tr><td>1</td><td>2</td></tr>
</table>
</body>
</html>
"""

_CH2 = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<body>
<h1 id="sec">Chapter Two</h1>
<p>Second chapter.</p>
<ul><li>alpha</li><li>beta</li></ul>
</body>
</html>
"""

_ENCRYPTION = """<?xml version="1.0"?>
<encryption xmlns="urn:oasis:names:tc:opendocument:xmlns:enc:1.0">
  <EncryptedData/>
</encryption>
"""


def build_minimal_epub(dest: Path, *, encrypted: bool = False) -> Path:
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(dest, "w") as zf:
        info = ZipInfo("mimetype")
        info.compress_type = ZIP_STORED
        zf.writestr(info, "application/epub+zip")
        zf.writestr("META-INF/container.xml", _CONTAINER, compress_type=ZIP_DEFLATED)
        if encrypted:
            zf.writestr("META-INF/encryption.xml", _ENCRYPTION, compress_type=ZIP_DEFLATED)
        zf.writestr("OEBPS/content.opf", _OPF, compress_type=ZIP_DEFLATED)
        zf.writestr("OEBPS/ch1.xhtml", _CH1, compress_type=ZIP_DEFLATED)
        zf.writestr("OEBPS/ch2.xhtml", _CH2, compress_type=ZIP_DEFLATED)
        zf.writestr("OEBPS/images/cover.png", MIN_PNG, compress_type=ZIP_DEFLATED)
    return dest
