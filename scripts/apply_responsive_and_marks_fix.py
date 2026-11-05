import json
import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. FIX CSS: Replace overflow-x: hidden on body with responsive clip
old_css = """    html, body {
      max-width: 100vw;
      overflow-x: hidden;
      position: relative;
      margin: 0;
      padding: 0;
    }
    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f8fafc;
      color: #0f172a;
      width: 100%;
    }"""

new_css = """    html {
      overflow-x: clip;
    }
    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f8fafc;
      color: #0f172a;
      width: 100%;
      overflow-x: clip;
      margin: 0;
      padding: 0;
    }"""

assert old_css in html, "CSS target not found"
html = html.replace(old_css, new_css)

# 2. UPDATE TOP NAVBAR WITH COMPLETE RESPONSIVE DESKTOP + MOBILE DRAWER (NO CUTOFFS)
old_navbar_pattern = re.compile(r"  <!-- TOP NAVBAR -->\s*<header[\s\S]*?</header>", re.MULTILINE)
assert old_navbar_pattern.search(html), "Old navbar not found"

new_navbar = """  <!-- TOP NAVBAR -->
  <header class="sticky top-0 z-50 backdrop-blur-md bg-white/95 border-b border-slate-200/80 px-3 sm:px-6 py-2.5 shadow-sm no-print">
    <div class="max-w-7xl mx-auto flex items-center justify-between gap-2 w-full">
      <!-- Logo + Title -->
      <div class="flex items-center space-x-2 shrink-0">
        <div class="h-8 w-8 sm:h-9 sm:w-9 rounded-2xl bg-gradient-to-tr from-orange-500 to-amber-500 flex items-center justify-center text-white shadow-md shadow-orange-500/30 shrink-0">
          <i data-lucide="sparkles" class="w-4 h-4 sm:w-4.5 sm:h-4.5"></i>
        </div>
        <div>
          <div class="flex items-center space-x-1.5">
            <h1 class="text-sm sm:text-base md:text-lg font-black tracking-tight text-slate-900 whitespace-nowrap">ExamForge<span class="text-orange-600">.AI</span></h1>
            <span class="clay-badge-mint text-[9px] sm:text-[10px] font-extrabold px-1.5 py-0.5 rounded-full whitespace-nowrap">BISEP 2026</span>
          </div>
          <p class="text-[10px] text-slate-500 hidden xl:block whitespace-nowrap">KPK Peshawar Board Class 1st to 10th Real Textbooks</p>
        </div>
      </div>

      <!-- DESKTOP ACTIONS (Screens >= 1024px) -->
      <div class="hidden lg:flex items-center gap-1.5 xl:gap-2 shrink-0">
        <!-- Guest status indicator -->
        <div id="nav-guest-status" class="flex items-center space-x-1 px-2.5 py-1.5 rounded-xl bg-emerald-50 border border-emerald-200 text-xs font-bold text-emerald-800 shrink-0">
          <i data-lucide="zap" class="w-3.5 h-3.5 text-emerald-600"></i>
          <span id="guest-quota-badge">Guest Free Access</span>
        </div>

        <!-- KPK Books -->
        <button onclick="openTextbookLibraryModal()" class="clay-btn-secondary bg-emerald-50/90 border-emerald-300 text-emerald-800 hover:bg-emerald-100 px-2.5 py-1.5 text-xs font-black flex items-center space-x-1 shrink-0" title="Browse all 70 KPK Textbooks for Class 1st to 10th">
          <i data-lucide="book-open" class="w-3.5 h-3.5 text-emerald-600"></i>
          <span>KPK Books (1-10)</span>
        </button>

        <!-- Paper Generator -->
        <button onclick="scrollToSection('generator')" class="clay-btn-secondary bg-orange-50/80 border-orange-200 text-orange-800 hover:bg-orange-100 px-2.5 py-1.5 text-xs font-black flex items-center space-x-1 shrink-0" title="Jump to Paper Generator">
          <i data-lucide="file-text" class="w-3.5 h-3.5 text-orange-600"></i>
          <span>Generator</span>
        </button>

        <!-- Magic Tool -->
        <button onclick="openMagicOcrModal()" class="clay-btn-secondary bg-gradient-to-r from-purple-50 to-indigo-50 border-purple-200 text-purple-700 hover:from-purple-100 hover:to-indigo-100 px-2.5 py-1.5 text-xs font-black flex items-center space-x-1 shrink-0" title="Upload picture of handwritten paper and convert to Word">
          <i data-lucide="wand-2" class="w-3.5 h-3.5 text-purple-600"></i>
          <span>Magic</span>
          <span class="bg-purple-600 text-white text-[8px] font-black px-1 py-0.5 rounded-full uppercase">OCR</span>
        </button>

        <!-- School Signed In Status -->
        <div id="nav-school-status" class="hidden flex items-center gap-1.5 shrink-0">
          <div class="clay-card-flat px-2 py-1 rounded-xl flex items-center space-x-1.5 border border-orange-200 bg-orange-50/50 shrink-0">
            <div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
            <span id="nav-school-name" class="text-xs font-black text-slate-900 max-w-[120px] truncate">School Portal</span>
          </div>
          <button onclick="openChangePasswordModal('school')" title="Change School Password" class="px-2 py-1.5 rounded-xl bg-orange-50 text-orange-700 hover:bg-orange-100 transition border border-orange-200 shrink-0 flex items-center space-x-1 text-xs font-bold">
            <i data-lucide="key-round" class="w-3.5 h-3.5 text-orange-600"></i>
            <span>Password</span>
          </button>
          <button onclick="handleSchoolLogout()" title="Sign Out" class="p-1.5 rounded-xl text-slate-500 hover:text-red-600 hover:bg-red-50 transition border border-slate-200 shrink-0">
            <i data-lucide="log-out" class="w-3.5 h-3.5"></i>
          </button>
        </div>

        <!-- School Sign In Button -->
        <button onclick="openSchoolLoginModal('school')" id="btn-nav-login" class="clay-btn-secondary px-2.5 py-1.5 text-xs font-bold flex items-center space-x-1 shrink-0">
          <i data-lucide="log-in" class="w-3.5 h-3.5 text-slate-700"></i>
          <span>School Sign In</span>
        </button>

        <!-- Muhammad Ali Owner Portal Button -->
        <button onclick="openOwnerMasterModal()" class="clay-btn-primary px-3 py-1.5 text-xs font-bold flex items-center space-x-1 shrink-0 shadow-sm">
          <i data-lucide="shield-check" class="w-3.5 h-3.5"></i>
          <span>Owner Portal</span>
        </button>
      </div>

      <!-- MOBILE / TABLET RIGHT ACTIONS (Screens < 1024px) -->
      <div class="flex lg:hidden items-center gap-1.5 shrink-0">
        <!-- Quick Owner Button -->
        <button onclick="openOwnerMasterModal()" class="clay-btn-primary px-2.5 py-1.5 text-xs font-bold flex items-center space-x-1 shadow-sm shrink-0">
          <i data-lucide="shield-check" class="w-3.5 h-3.5"></i>
          <span>Owner</span>
        </button>

        <!-- Mobile Hamburger Button -->
        <button type="button" onclick="toggleMobileNavMenu()" class="p-2 rounded-xl border border-slate-200 bg-white text-slate-700 hover:bg-orange-50 hover:text-orange-600 transition shrink-0" aria-label="Toggle navigation menu">
          <i data-lucide="menu" id="mobile-menu-icon" class="w-5 h-5"></i>
        </button>
      </div>
    </div>

    <!-- MOBILE DROPDOWN DRAWER (Collapsible, no horizontal overflow) -->
    <div id="mobile-nav-drawer" class="hidden lg:hidden border-t border-slate-200/90 mt-2.5 pt-3 space-y-2">
      <div class="grid grid-cols-2 gap-2">
        <button onclick="openTextbookLibraryModal(); closeMobileNavMenu();" class="p-2.5 rounded-xl border border-emerald-200 bg-emerald-50 text-emerald-800 text-xs font-bold flex items-center space-x-2">
          <i data-lucide="book-open" class="w-4 h-4 text-emerald-600"></i>
          <span>KPK Books (1-10)</span>
        </button>
        <button onclick="scrollToSection('generator'); closeMobileNavMenu();" class="p-2.5 rounded-xl border border-orange-200 bg-orange-50 text-orange-800 text-xs font-bold flex items-center space-x-2">
          <i data-lucide="file-text" class="w-4 h-4 text-orange-600"></i>
          <span>Paper Generator</span>
        </button>
        <button onclick="openMagicOcrModal(); closeMobileNavMenu();" class="p-2.5 rounded-xl border border-purple-200 bg-purple-50 text-purple-800 text-xs font-bold flex items-center space-x-2">
          <i data-lucide="wand-2" class="w-4 h-4 text-purple-600"></i>
          <span>Magic OCR Tool</span>
        </button>
        <button onclick="openEditMarksModal(); closeMobileNavMenu();" class="p-2.5 rounded-xl border border-amber-200 bg-amber-50 text-amber-800 text-xs font-bold flex items-center space-x-2">
          <i data-lucide="award" class="w-4 h-4 text-amber-600"></i>
          <span>Change Marks</span>
        </button>
      </div>

      <div class="pt-1 flex flex-col gap-1.5">
        <!-- School Login / Account in Mobile -->
        <div id="nav-school-status-mobile" class="hidden flex items-center justify-between p-2 rounded-xl bg-orange-50 border border-orange-200">
          <div class="flex items-center space-x-1.5">
            <div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
            <span id="nav-school-name-mobile" class="text-xs font-bold text-slate-900">School Portal</span>
          </div>
          <div class="flex items-center space-x-1">
            <button onclick="openChangePasswordModal('school'); closeMobileNavMenu();" class="px-2 py-1 text-[11px] font-bold rounded-lg bg-white border border-slate-200 text-slate-700">Key</button>
            <button onclick="handleSchoolLogout(); closeMobileNavMenu();" class="p-1 text-red-600 hover:bg-red-100 rounded-lg"><i data-lucide="log-out" class="w-4 h-4"></i></button>
          </div>
        </div>
        <button onclick="openSchoolLoginModal('school'); closeMobileNavMenu();" id="btn-nav-login-mobile" class="w-full py-2.5 px-3 rounded-xl border border-slate-200 bg-slate-50 text-slate-800 text-xs font-bold flex items-center justify-center space-x-2">
          <i data-lucide="log-in" class="w-4 h-4 text-slate-600"></i>
          <span>School Account Sign In</span>
        </button>
        <button onclick="openChangePasswordModal(); closeMobileNavMenu();" class="w-full py-2 px-3 rounded-xl border border-slate-200 bg-white text-slate-600 text-xs font-bold flex items-center justify-center space-x-2">
          <i data-lucide="key-round" class="w-3.5 h-3.5"></i>
          <span>Change Account / Master Password</span>
        </button>
      </div>
    </div>
  </header>"""

html = old_navbar_pattern.sub(new_navbar, html, count=1)

# 3. ADD COMPREHENSIVE MARKS & WEIGHTAGE MODAL
marks_modal_html = """
  <!-- COMPREHENSIVE MARKS & WEIGHTAGE EDITOR MODAL -->
  <div id="edit-marks-modal" class="fixed inset-0 z-50 bg-slate-900/80 backdrop-blur-md hidden flex items-center justify-center p-3 sm:p-6 no-print">
    <div class="clay-card max-w-lg w-full p-6 sm:p-8 relative space-y-5 animate-in fade-in zoom-in-95 duration-200 max-h-[92vh] overflow-y-auto">
      <button onclick="closeEditMarksModal()" class="absolute top-4 right-4 text-slate-400 hover:text-slate-600 p-1">
        <i data-lucide="x" class="w-5 h-5"></i>
      </button>

      <div class="space-y-1 border-b border-slate-200 pb-3">
        <div class="inline-flex items-center space-x-1.5 clay-badge-orange px-2.5 py-0.5 rounded-full text-[11px] font-black mb-1">
          <i data-lucide="award" class="w-3.5 h-3.5 text-orange-600"></i>
          <span>Custom Marks & Scoring Scheme</span>
        </div>
        <h4 class="text-xl font-black text-slate-900">Change Paper & Section Marks</h4>
        <p class="text-xs text-slate-500">Customize the exact marks for every section and question. All totals and Word export will update automatically.</p>
      </div>

      <form id="edit-marks-form" onsubmit="handleApplyCustomMarksModal(event)" class="space-y-4">
        
        <!-- Total Marks & Presets -->
        <div class="clay-card-flat p-3 rounded-xl space-y-2 bg-orange-50/50 border border-orange-200">
          <div class="flex items-center justify-between">
            <span class="text-xs font-black text-slate-900">Total Paper Marks:</span>
            <span id="modal-marks-total-badge" class="clay-badge-orange text-xs font-mono font-black px-2.5 py-0.5 rounded-full">75 Marks</span>
          </div>
          <div class="grid grid-cols-4 gap-1.5">
            <button type="button" onclick="setModalMarksPreset(50)" class="py-1 px-2 text-xs font-bold rounded-lg border border-slate-200 bg-white hover:bg-orange-50 text-slate-700">50 M</button>
            <button type="button" onclick="setModalMarksPreset(75)" class="py-1 px-2 text-xs font-bold rounded-lg border border-orange-500 bg-orange-100 text-orange-900 font-black">75 M</button>
            <button type="button" onclick="setModalMarksPreset(100)" class="py-1 px-2 text-xs font-bold rounded-lg border border-slate-200 bg-white hover:bg-orange-50 text-slate-700">100 M</button>
            <button type="button" onclick="setModalMarksPreset(25)" class="py-1 px-2 text-xs font-bold rounded-lg border border-slate-200 bg-white hover:bg-orange-50 text-slate-700">25 M</button>
          </div>
        </div>

        <!-- Section Marks Allocation Inputs -->
        <div class="space-y-3 text-xs">
          <!-- Section A -->
          <div class="flex items-center justify-between p-2.5 rounded-xl border border-slate-200 bg-white gap-2">
            <div>
              <span class="font-extrabold text-slate-900 block">Section A: Objective (MCQs) Marks</span>
              <span class="text-[10px] text-slate-500">Total marks assigned to Section A</span>
            </div>
            <div class="flex items-center space-x-1 shrink-0">
              <input type="number" id="modal-marks-sec-a" min="1" max="100" value="15" oninput="recalcModalTotal()" class="w-16 clay-input p-1.5 text-center font-bold text-xs" />
              <span class="font-bold text-slate-400">M</span>
            </div>
          </div>

          <!-- Section B -->
          <div class="flex items-center justify-between p-2.5 rounded-xl border border-slate-200 bg-white gap-2">
            <div>
              <span class="font-extrabold text-slate-900 block">Section B: Short Questions Marks</span>
              <span class="text-[10px] text-slate-500">Total marks assigned to Section B</span>
            </div>
            <div class="flex items-center space-x-1 shrink-0">
              <input type="number" id="modal-marks-sec-b" min="1" max="100" value="36" oninput="recalcModalTotal()" class="w-16 clay-input p-1.5 text-center font-bold text-xs" />
              <span class="font-bold text-slate-400">M</span>
            </div>
          </div>

          <!-- Section C -->
          <div class="flex items-center justify-between p-2.5 rounded-xl border border-slate-200 bg-white gap-2">
            <div>
              <span class="font-extrabold text-slate-900 block">Section C: Long Questions Marks</span>
              <span class="text-[10px] text-slate-500">Total marks assigned to Section C</span>
            </div>
            <div class="flex items-center space-x-1 shrink-0">
              <input type="number" id="modal-marks-sec-c" min="0" max="100" value="24" oninput="recalcModalTotal()" class="w-16 clay-input p-1.5 text-center font-bold text-xs" />
              <span class="font-bold text-slate-400">M</span>
            </div>
          </div>

          <!-- Marks Per Individual Question -->
          <div class="grid grid-cols-2 gap-2 pt-1">
            <div class="p-2 rounded-xl border border-slate-200 bg-slate-50 space-y-1">
              <label class="block text-[10px] font-bold text-slate-700">Marks per Short Q:</label>
              <input type="number" id="modal-marks-per-short" min="1" max="20" value="4" class="w-full clay-input p-1.5 text-center font-bold text-xs" />
            </div>
            <div class="p-2 rounded-xl border border-slate-200 bg-slate-50 space-y-1">
              <label class="block text-[10px] font-bold text-slate-700">Marks per Long Q:</label>
              <input type="number" id="modal-marks-per-long" min="1" max="30" value="8" class="w-full clay-input p-1.5 text-center font-bold text-xs" />
            </div>
          </div>

          <!-- Marks Display Style -->
          <div class="space-y-1 pt-1">
            <label class="block text-[11px] font-bold text-slate-700">Marks Display Style:</label>
            <select id="modal-marks-display-style" class="w-full clay-input p-2 text-xs font-bold text-slate-800">
              <option value="school-per-question">🏫 School Style: Show marks badge on every question [4 Marks ✏️]</option>
              <option value="bisep-header-only">🏛 BISEP Style: Show marks in section headers only</option>
              <option value="compact-score">📝 Minimalist: Show compact marks (4) at end</option>
            </select>
          </div>
        </div>

        <button type="submit" class="w-full clay-btn-primary py-3 px-4 text-xs font-black flex items-center justify-center space-x-2 shadow-md">
          <i data-lucide="check" class="w-4 h-4"></i>
          <span>Apply Marks & Recalculate Paper</span>
        </button>
      </form>
    </div>
  </div>
"""

# Insert marks modal right after footer tag
footer_tag = "  </footer>"
assert footer_tag in html, "Footer tag not found"
html = html.replace(footer_tag, footer_tag + "\n" + marks_modal_html)

# 4. UPDATE SECTION HEADERS IN SHEET A AND SHEET BC WITH CLICKABLE MARKS BUTTONS
old_sec_a_header = """            <div class="bg-slate-900 text-white px-3.5 py-1.5 rounded text-xs font-black tracking-wide flex items-center justify-between">
              <span>SECTION — A (Objective Multiple Choice Questions)</span>
              <span>Marks: <span id="sec-a-marks" contenteditable="true" onblur="updateSectionMarks('A', this.innerText)" class="editable-text text-amber-300">15</span></span>
            </div>"""

new_sec_a_header = """            <div class="bg-slate-900 text-white px-3.5 py-1.5 rounded text-xs font-black tracking-wide flex items-center justify-between">
              <span>SECTION — A (Objective Multiple Choice Questions)</span>
              <button type="button" onclick="openEditMarksModal('A')" class="bg-amber-400/20 hover:bg-amber-400/40 text-amber-300 font-mono font-black px-2 py-0.5 rounded border border-amber-400/50 cursor-pointer inline-flex items-center space-x-1" title="Click to change Section A Marks">
                <span>Marks:</span> <span id="sec-a-marks">15</span> <i data-lucide="edit-3" class="w-3 h-3 ml-1 text-amber-200"></i>
              </button>
            </div>"""

if old_sec_a_header in html:
    html = html.replace(old_sec_a_header, new_sec_a_header)

old_sec_b_header = """            <div class="bg-slate-900 text-white px-3.5 py-1.5 rounded text-xs font-black tracking-wide flex items-center justify-between">
              <span>SECTION — B (Short Conceptual Questions)</span>
              <span>Marks: <span id="sec-b-marks" contenteditable="true" onblur="updateSectionMarks('B', this.innerText)" class="editable-text text-amber-300">36</span></span>
            </div>"""

new_sec_b_header = """            <div class="bg-slate-900 text-white px-3.5 py-1.5 rounded text-xs font-black tracking-wide flex items-center justify-between">
              <span>SECTION — B (Short Conceptual Questions)</span>
              <button type="button" onclick="openEditMarksModal('B')" class="bg-amber-400/20 hover:bg-amber-400/40 text-amber-300 font-mono font-black px-2 py-0.5 rounded border border-amber-400/50 cursor-pointer inline-flex items-center space-x-1" title="Click to change Section B Marks">
                <span>Marks:</span> <span id="sec-b-marks">36</span> <i data-lucide="edit-3" class="w-3 h-3 ml-1 text-amber-200"></i>
              </button>
            </div>"""

if old_sec_b_header in html:
    html = html.replace(old_sec_b_header, new_sec_b_header)

old_sec_c_header = """            <div class="bg-slate-900 text-white px-3.5 py-1.5 rounded text-xs font-black tracking-wide flex items-center justify-between">
              <span>SECTION — C (Descriptive Long Questions)</span>
              <span>Marks: <span id="sec-c-marks" contenteditable="true" onblur="updateSectionMarks('C', this.innerText)" class="editable-text text-amber-300">24</span></span>
            </div>"""

new_sec_c_header = """            <div class="bg-slate-900 text-white px-3.5 py-1.5 rounded text-xs font-black tracking-wide flex items-center justify-between">
              <span>SECTION — C (Descriptive Long Questions)</span>
              <button type="button" onclick="openEditMarksModal('C')" class="bg-amber-400/20 hover:bg-amber-400/40 text-amber-300 font-mono font-black px-2 py-0.5 rounded border border-amber-400/50 cursor-pointer inline-flex items-center space-x-1" title="Click to change Section C Marks">
                <span>Marks:</span> <span id="sec-c-marks">24</span> <i data-lucide="edit-3" class="w-3 h-3 ml-1 text-amber-200"></i>
              </button>
            </div>"""

if old_sec_c_header in html:
    html = html.replace(old_sec_c_header, new_sec_c_header)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Applied navbar, modal, and headers successfully!")
