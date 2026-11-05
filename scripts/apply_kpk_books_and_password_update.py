import json
import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. FIX NAVBAR OVERFLOW
old_navbar = """    <div class="max-w-7xl mx-auto flex flex-wrap sm:flex-nowrap items-center justify-between gap-2.5">
      <div class="flex items-center space-x-2.5 sm:space-x-3">
        <div class="h-9 w-9 sm:h-10 sm:w-10 rounded-2xl bg-gradient-to-tr from-orange-500 to-amber-500 flex items-center justify-center text-white shadow-md shadow-orange-500/30 shrink-0">
          <i data-lucide="sparkles" class="w-4 h-4 sm:w-5 sm:h-5"></i>
        </div>
        <div>
          <div class="flex items-center space-x-1.5 sm:space-x-2">
            <h1 class="text-base sm:text-lg font-black tracking-tight text-slate-900">ExamForge<span class="text-orange-600">.AI</span></h1>
            <span class="clay-badge-mint text-[9px] sm:text-[10px] font-extrabold px-1.5 sm:px-2 py-0.5 rounded-full">BISEP 2026</span>
          </div>
          <p class="text-[10px] sm:text-[11px] font-medium text-slate-500 hidden md:block">KPK Textbook Board Class 9th & 10th Examination System</p>
        </div>
      </div>

      <!-- Action buttons & Auth states -->
      <div class="flex items-center space-x-1.5 sm:space-x-2.5 flex-wrap">
        <!-- Guest status indicator -->
        <div id="nav-guest-status" class="flex items-center space-x-1 px-2.5 sm:px-3 py-1.5 rounded-xl bg-emerald-50 border border-emerald-200 text-[11px] sm:text-xs font-bold text-emerald-800">
          <i data-lucide="zap" class="w-3.5 h-3.5 text-emerald-600"></i>
          <span id="guest-quota-badge" class="hidden sm:inline">Guest Free Access: Instant Paper Generation</span>
          <span class="sm:hidden font-extrabold text-[10px]">Free Guest</span>
        </div>

        <!-- Paper Generator Quick Navigation -->
        <button onclick="scrollToSection('generator')" class="clay-btn-secondary bg-orange-50/80 border-orange-200 text-orange-800 hover:bg-orange-100 px-2.5 sm:px-3 py-1.5 sm:py-2 text-[11px] sm:text-xs font-black flex items-center space-x-1 sm:space-x-1.5 shadow-sm" title="Jump to Class 9th & 10th Paper Generator">
          <i data-lucide="file-text" class="w-3.5 h-3.5 sm:w-4 sm:h-4 text-orange-600"></i>
          <span>Paper Generator</span>
        </button>

        <!-- Magic Tool Button (New!) -->
        <button onclick="openMagicOcrModal()" class="clay-btn-secondary bg-gradient-to-r from-purple-50 to-indigo-50 border-purple-200 text-purple-700 hover:from-purple-100 hover:to-indigo-100 px-2.5 sm:px-3.5 py-1.5 sm:py-2 text-[11px] sm:text-xs font-black flex items-center space-x-1.5 shadow-sm" title="Upload picture of handwritten paper and convert to formatted Word document">
          <i data-lucide="wand-2" class="w-3.5 h-3.5 sm:w-4 sm:h-4 text-purple-600"></i>
          <span>Magic Tool</span>
          <span class="bg-purple-600 text-white text-[8px] sm:text-[9px] font-black px-1.5 py-0.5 rounded-full uppercase tracking-wider">OCR</span>
        </button>

        <!-- School Signed In Status (Hidden by default) -->
        <div id="nav-school-status" class="hidden flex items-center space-x-1.5 sm:space-x-2">
          <div class="clay-card-flat px-2 sm:px-3 py-1 rounded-xl flex items-center space-x-1.5 border border-orange-200 bg-orange-50/50">
            <div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
            <span id="nav-school-name" class="text-xs font-black text-slate-900 max-w-[110px] sm:max-w-[150px] truncate">School Portal</span>
            <span class="clay-badge-mint text-[9px] font-bold px-1.5 py-0.5 rounded-full hidden sm:inline">Pro School</span>
          </div>
          <button onclick="handleSchoolLogout()" title="Sign Out" class="p-1.5 sm:p-2 rounded-xl text-slate-500 hover:text-red-600 hover:bg-red-50 transition border border-slate-200">
            <i data-lucide="log-out" class="w-3.5 h-3.5 sm:w-4 sm:h-4"></i>
          </button>
        </div>

        <!-- School Sign In Button -->
        <button onclick="openSchoolLoginModal()" id="btn-nav-login" class="clay-btn-secondary px-2.5 sm:px-3.5 py-1.5 sm:py-2 text-[11px] sm:text-xs font-bold flex items-center space-x-1 sm:space-x-1.5">
          <i data-lucide="log-in" class="w-3.5 h-3.5 sm:w-4 sm:h-4 text-slate-700"></i>
          <span class="hidden sm:inline">School Sign In</span>
          <span class="sm:hidden">Sign In</span>
        </button>

        <!-- Muhammad Ali Owner Portal Button -->
        <button onclick="openOwnerMasterModal()" class="clay-btn-primary px-2.5 sm:px-3.5 py-1.5 sm:py-2 text-[11px] sm:text-xs font-bold flex items-center space-x-1 sm:space-x-1.5 shadow-sm">
          <i data-lucide="shield-check" class="w-3.5 h-3.5 sm:w-4 sm:h-4"></i>
          <span class="hidden sm:inline">Owner Portal</span>
          <span class="sm:hidden">Owner</span>
        </button>
      </div>
    </div>"""

new_navbar = """    <div class="max-w-7xl mx-auto flex items-center justify-between gap-2 w-full">
      <div class="flex items-center space-x-2 sm:space-x-2.5 shrink-0">
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

      <!-- Action buttons & Auth states (Strictly single-line, flex-nowrap, no overflow onto second line) -->
      <div class="flex items-center gap-1 sm:gap-2 flex-nowrap shrink-0 overflow-x-auto no-scrollbar py-0.5">
        <!-- Guest status indicator -->
        <div id="nav-guest-status" class="hidden lg:flex items-center space-x-1 px-2.5 py-1.5 rounded-xl bg-emerald-50 border border-emerald-200 text-xs font-bold text-emerald-800 shrink-0 whitespace-nowrap">
          <i data-lucide="zap" class="w-3.5 h-3.5 text-emerald-600"></i>
          <span id="guest-quota-badge">Guest Free Access</span>
        </div>

        <!-- KPK Textbooks Library Quick Button (Classes 1st to 10th) -->
        <button onclick="openTextbookLibraryModal()" class="clay-btn-secondary bg-emerald-50/90 border-emerald-300 text-emerald-800 hover:bg-emerald-100 px-2 sm:px-2.5 py-1.5 text-xs font-black flex items-center space-x-1 shrink-0 whitespace-nowrap" title="Browse all 70 KPK Textbooks for Class 1st to 10th">
          <i data-lucide="book-open" class="w-3.5 h-3.5 text-emerald-600"></i>
          <span class="hidden md:inline">KPK Books (1-10)</span>
          <span class="md:hidden">Books</span>
        </button>

        <!-- Paper Generator Quick Navigation -->
        <button onclick="scrollToSection('generator')" class="clay-btn-secondary bg-orange-50/80 border-orange-200 text-orange-800 hover:bg-orange-100 px-2 sm:px-2.5 py-1.5 text-xs font-black flex items-center space-x-1 shrink-0 whitespace-nowrap" title="Jump to Paper Generator">
          <i data-lucide="file-text" class="w-3.5 h-3.5 text-orange-600"></i>
          <span class="hidden sm:inline">Generator</span>
          <span class="sm:hidden">Gen</span>
        </button>

        <!-- Magic Tool Button -->
        <button onclick="openMagicOcrModal()" class="clay-btn-secondary bg-gradient-to-r from-purple-50 to-indigo-50 border-purple-200 text-purple-700 hover:from-purple-100 hover:to-indigo-100 px-2 sm:px-2.5 py-1.5 text-xs font-black flex items-center space-x-1 shrink-0 whitespace-nowrap" title="Upload picture of handwritten paper and convert to Word">
          <i data-lucide="wand-2" class="w-3.5 h-3.5 text-purple-600"></i>
          <span>Magic</span>
          <span class="bg-purple-600 text-white text-[8px] font-black px-1 py-0.5 rounded-full uppercase">OCR</span>
        </button>

        <!-- School Signed In Status (Hidden by default) -->
        <div id="nav-school-status" class="hidden flex items-center gap-1 sm:gap-1.5 shrink-0">
          <div class="clay-card-flat px-2 py-1 rounded-xl flex items-center space-x-1.5 border border-orange-200 bg-orange-50/50 shrink-0">
            <div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
            <span id="nav-school-name" class="text-xs font-black text-slate-900 max-w-[90px] sm:max-w-[130px] truncate">School Portal</span>
          </div>
          <!-- Change Password Button for Logged in School -->
          <button onclick="openChangePasswordModal('school')" title="Change School Password" class="px-2 py-1.5 rounded-xl bg-orange-50 text-orange-700 hover:bg-orange-100 transition border border-orange-200 shrink-0 flex items-center space-x-1 text-xs font-bold whitespace-nowrap">
            <i data-lucide="key-round" class="w-3.5 h-3.5 text-orange-600"></i>
            <span class="hidden lg:inline">Password</span>
          </button>
          <button onclick="handleSchoolLogout()" title="Sign Out" class="p-1.5 rounded-xl text-slate-500 hover:text-red-600 hover:bg-red-50 transition border border-slate-200 shrink-0">
            <i data-lucide="log-out" class="w-3.5 h-3.5"></i>
          </button>
        </div>

        <!-- School Sign In Button -->
        <button onclick="openSchoolLoginModal('school')" id="btn-nav-login" class="clay-btn-secondary px-2 sm:px-2.5 py-1.5 text-xs font-bold flex items-center space-x-1 shrink-0 whitespace-nowrap">
          <i data-lucide="log-in" class="w-3.5 h-3.5 text-slate-700"></i>
          <span class="hidden sm:inline">School Sign In</span>
          <span class="sm:hidden">Sign In</span>
        </button>

        <!-- Muhammad Ali Owner Portal Button -->
        <button onclick="openOwnerMasterModal()" class="clay-btn-primary px-2.5 sm:px-3 py-1.5 text-xs font-bold flex items-center space-x-1 shrink-0 whitespace-nowrap shadow-sm">
          <i data-lucide="shield-check" class="w-3.5 h-3.5"></i>
          <span class="hidden sm:inline">Owner Portal</span>
          <span class="sm:hidden">Owner</span>
        </button>
      </div>
    </div>"""

assert old_navbar in html, "Navbar target not found"
html = html.replace(old_navbar, new_navbar)

# 2. EXPAND TARGET CLASS SELECTOR (CLASSES 1 TO 10)
old_grade_sel = """              <label class="block text-xs font-bold text-slate-700 mb-1">Target Class</label>
              <select id="gen-grade" onchange="handleGradeChange()" class="w-full clay-input p-2.5 text-xs font-bold text-slate-800">
                <option value="9">Class 9th (Matric-I)</option>
                <option value="10">Class 10th (Matric-II)</option>
              </select>"""

new_grade_sel = """              <label class="block text-xs font-bold text-slate-700 mb-1">Target Class</label>
              <select id="gen-grade" onchange="handleGradeChange()" class="w-full clay-input p-2.5 text-xs font-bold text-slate-800">
                <option value="1">Class 1st (Primary)</option>
                <option value="2">Class 2nd (Primary)</option>
                <option value="3">Class 3rd (Primary)</option>
                <option value="4">Class 4th (Primary)</option>
                <option value="5">Class 5th (Primary)</option>
                <option value="6">Class 6th (Middle)</option>
                <option value="7">Class 7th (Middle)</option>
                <option value="8">Class 8th (Middle)</option>
                <option value="9" selected>Class 9th (Matric-I)</option>
                <option value="10">Class 10th (Matric-II)</option>
              </select>"""

assert old_grade_sel in html, "Grade selector target not found"
html = html.replace(old_grade_sel, new_grade_sel)

# 3. REMOVE STRAY CLOSING TAGS BEFORE OWNER MASTER MODAL
stray_tags = """        <div class="text-center text-xs text-slate-400 pt-1">
          <span>Protected site owner console &bull; ExamForge AI Peshawar</span>
        </div>
      </form>
    </div>
  </div>
      </form>
    </div>
  </div>

  <!-- MUHAMMAD ALI OWNER MASTER PORTAL (CREATE & MANAGE SCHOOL ACCOUNTS) -->"""

fixed_tags = """        <div class="text-center text-xs text-slate-400 pt-1">
          <span>Protected site owner console &bull; ExamForge AI Peshawar</span>
        </div>
      </form>
    </div>
  </div>

  <!-- MUHAMMAD ALI OWNER MASTER PORTAL (CREATE & MANAGE SCHOOL ACCOUNTS) -->"""

assert stray_tags in html, "Stray tags target not found"
html = html.replace(stray_tags, fixed_tags)

# 4. ADD CHANGE MASTER PASSWORD CARD INSIDE OWNER MASTER MODAL
old_owner_header_end = """      <!-- Action Toast Notice -->
      <div id="owner-toast" class="hidden p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs font-bold text-emerald-800 flex items-center space-x-2">
        <i data-lucide="check-circle" class="w-4 h-4 text-emerald-600"></i>
        <span id="owner-toast-text">School account created successfully!</span>
      </div>"""

new_owner_header_end = """      <!-- Action Toast Notice -->
      <div id="owner-toast" class="hidden p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs font-bold text-emerald-800 flex items-center space-x-2">
        <i data-lucide="check-circle" class="w-4 h-4 text-emerald-600"></i>
        <span id="owner-toast-text">School account created successfully!</span>
      </div>

      <!-- CHANGE OWNER MASTER PASSWORD CARD -->
      <div class="clay-card-flat p-4 rounded-2xl border border-slate-200 bg-slate-50/70 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 rounded-xl bg-orange-100 flex items-center justify-center text-orange-600 shrink-0">
            <i data-lucide="key-round" class="w-5 h-5"></i>
          </div>
          <div>
            <h5 class="text-xs font-black text-slate-900">Owner Master Password</h5>
            <p class="text-[11px] text-slate-500">Update the master password used to unlock this Owner Section on all devices.</p>
          </div>
        </div>
        <button type="button" onclick="openChangePasswordModal('owner')" class="clay-btn-secondary px-3.5 py-2 text-xs font-bold flex items-center space-x-1.5 shrink-0 whitespace-nowrap">
          <i data-lucide="shield-check" class="w-4 h-4 text-orange-600"></i>
          <span>Change Master Password</span>
        </button>
      </div>"""

assert old_owner_header_end in html, "Owner header end target not found"
html = html.replace(old_owner_header_end, new_owner_header_end)

# Also update footer github link to paper_gen
html = html.replace("https://github.com/alikhan14756/prompt", "https://github.com/alikhan14756/paper_gen")

# 5. INSERT CHANGE PASSWORD MODAL AND TEXTBOOK LIBRARY MODAL RIGHT AFTER </footer>
footer_tag = "  </footer>"
assert footer_tag in html, "</footer> tag not found"

modals_html = """
  <!-- CHANGE PASSWORD MODAL (UNIVERSAL FOR SCHOOL & OWNER) -->
  <div id="change-password-modal" class="fixed inset-0 z-50 bg-slate-900/80 backdrop-blur-md hidden flex items-center justify-center p-3 sm:p-6 no-print">
    <div class="clay-card max-w-md w-full p-6 sm:p-8 relative space-y-5 animate-in fade-in zoom-in-95 duration-200">
      <button onclick="closeChangePasswordModal()" class="absolute top-4 right-4 text-slate-400 hover:text-slate-600 p-1">
        <i data-lucide="x" class="w-5 h-5"></i>
      </button>

      <div class="text-center space-y-2">
        <div class="inline-flex h-12 w-12 rounded-2xl bg-orange-100 items-center justify-center text-orange-600 mb-1">
          <i data-lucide="key-round" class="w-6 h-6"></i>
        </div>
        <h4 class="text-xl font-black text-slate-900">Change Account Password</h4>
        <p class="text-xs text-slate-500" id="change-pwd-subtitle">Update your secure login password. Synchronizes across all devices.</p>
        <div id="change-pwd-account-badge" class="inline-block clay-badge-orange text-[11px] font-bold px-3 py-1 rounded-full">
          Active Account: School Portal
        </div>
      </div>

      <div id="change-pwd-error" class="hidden p-3 rounded-xl bg-red-50 border border-red-200 text-xs font-semibold text-red-700"></div>
      <div id="change-pwd-success" class="hidden p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs font-semibold text-emerald-800"></div>

      <form id="change-password-form" onsubmit="handleChangePasswordSubmit(event)" class="space-y-4">
        <input type="hidden" id="change-pwd-role" value="school" />

        <!-- For unauthenticated users choosing who they are -->
        <div id="change-pwd-role-selector" class="hidden">
          <label class="block text-xs font-bold text-slate-700 mb-1">Select Account Type</label>
          <div class="grid grid-cols-2 gap-2">
            <button type="button" onclick="setChangePasswordRole('school')" id="role-btn-school" class="py-2 px-3 text-xs font-bold rounded-xl border border-orange-500 bg-orange-50 text-orange-800">🏫 School</button>
            <button type="button" onclick="setChangePasswordRole('owner')" id="role-btn-owner" class="py-2 px-3 text-xs font-bold rounded-xl border border-slate-200 bg-white text-slate-700">👑 Owner</button>
          </div>
        </div>

        <div id="change-pwd-school-username-group" class="hidden">
          <label class="block text-xs font-bold text-slate-700 mb-1">School Username *</label>
          <input type="text" id="change-pwd-username" placeholder="e.g. peshawarmodel" class="w-full clay-input p-2.5 text-xs font-bold text-slate-800" />
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Current Password *</label>
          <div class="relative">
            <i data-lucide="lock" class="w-4 h-4 text-slate-400 absolute left-3 top-3"></i>
            <input type="password" required id="change-pwd-current" placeholder="Enter current password" class="w-full clay-input pl-9 pr-10 p-2.5 text-xs font-bold text-slate-800" />
            <button type="button" onclick="togglePasswordVisibility('change-pwd-current', 'change-pwd-current-eye')" class="absolute right-3 top-2.5 text-slate-400 hover:text-slate-600 p-0.5">
              <i data-lucide="eye" id="change-pwd-current-eye" class="w-4 h-4"></i>
            </button>
          </div>
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">New Password *</label>
          <div class="relative">
            <i data-lucide="key" class="w-4 h-4 text-slate-400 absolute left-3 top-3"></i>
            <input type="password" required id="change-pwd-new" minlength="4" placeholder="Enter new strong password" class="w-full clay-input pl-9 pr-10 p-2.5 text-xs font-bold text-slate-800" />
            <button type="button" onclick="togglePasswordVisibility('change-pwd-new', 'change-pwd-new-eye')" class="absolute right-3 top-2.5 text-slate-400 hover:text-slate-600 p-0.5">
              <i data-lucide="eye" id="change-pwd-new-eye" class="w-4 h-4"></i>
            </button>
          </div>
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Confirm New Password *</label>
          <div class="relative">
            <i data-lucide="check" class="w-4 h-4 text-slate-400 absolute left-3 top-3"></i>
            <input type="password" required id="change-pwd-confirm" minlength="4" placeholder="Re-enter new password" class="w-full clay-input pl-9 pr-10 p-2.5 text-xs font-bold text-slate-800" />
            <button type="button" onclick="togglePasswordVisibility('change-pwd-confirm', 'change-pwd-confirm-eye')" class="absolute right-3 top-2.5 text-slate-400 hover:text-slate-600 p-0.5">
              <i data-lucide="eye" id="change-pwd-confirm-eye" class="w-4 h-4"></i>
            </button>
          </div>
        </div>

        <button type="submit" id="btn-submit-change-pwd" class="w-full clay-btn-primary py-3 px-4 text-xs font-black flex items-center justify-center space-x-2 shadow-md">
          <i data-lucide="save" class="w-4 h-4"></i>
          <span>Update Password & Sync Devices</span>
        </button>
      </form>
    </div>
  </div>

  <!-- KPK TEXTBOOK BOARD (BISEP) COMPLETE TEXTBOOK LIBRARY MODAL (CLASSES 1ST TO 10TH) -->
  <div id="textbook-library-modal" class="fixed inset-0 z-50 bg-slate-900/80 backdrop-blur-md hidden flex items-center justify-center p-3 sm:p-6 no-print">
    <div class="clay-card max-w-5xl w-full p-5 sm:p-7 relative space-y-5 max-h-[92vh] flex flex-col">
      <button onclick="closeTextbookLibraryModal()" class="absolute top-4 right-4 text-slate-400 hover:text-slate-600 p-1">
        <i data-lucide="x" class="w-6 h-6"></i>
      </button>

      <!-- Library Header -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 pb-4 shrink-0">
        <div>
          <div class="inline-flex items-center space-x-1.5 clay-badge-mint px-2.5 py-0.5 rounded-full text-[11px] font-black mb-1">
            <i data-lucide="book-open" class="w-3.5 h-3.5 text-emerald-700"></i>
            <span>Official Khyber Pakhtunkhwa Curriculum</span>
          </div>
          <h3 class="text-xl sm:text-2xl font-black text-slate-900">KPK Peshawar Board Complete Textbooks (Class 1st - 10th)</h3>
          <p class="text-xs text-slate-500">70 Official authentic textbooks ready to download as PDF or generate examination papers directly.</p>
        </div>
        <div class="flex items-center space-x-2 shrink-0">
          <span class="text-xs font-extrabold text-emerald-800 bg-emerald-50 px-3 py-1.5 rounded-xl border border-emerald-200">
            70 Real KPK Books Installed
          </span>
        </div>
      </div>

      <!-- Filters & Search Controls -->
      <div class="flex flex-wrap items-center justify-between gap-2.5 shrink-0 bg-slate-50 p-2.5 rounded-2xl border border-slate-200">
        <!-- Grade Filter Pills -->
        <div class="flex items-center space-x-1 overflow-x-auto no-scrollbar py-0.5 max-w-full">
          <button type="button" onclick="filterTextbookByGrade('all')" class="tb-grade-pill px-2.5 py-1 text-xs font-black rounded-lg transition bg-orange-600 text-white shadow-xs" data-grade="all">All</button>
          <button type="button" onclick="filterTextbookByGrade('1')" class="tb-grade-pill px-2 py-1 text-xs font-bold rounded-lg transition bg-white text-slate-700 hover:bg-slate-100" data-grade="1">Class 1</button>
          <button type="button" onclick="filterTextbookByGrade('2')" class="tb-grade-pill px-2 py-1 text-xs font-bold rounded-lg transition bg-white text-slate-700 hover:bg-slate-100" data-grade="2">Class 2</button>
          <button type="button" onclick="filterTextbookByGrade('3')" class="tb-grade-pill px-2 py-1 text-xs font-bold rounded-lg transition bg-white text-slate-700 hover:bg-slate-100" data-grade="3">Class 3</button>
          <button type="button" onclick="filterTextbookByGrade('4')" class="tb-grade-pill px-2 py-1 text-xs font-bold rounded-lg transition bg-white text-slate-700 hover:bg-slate-100" data-grade="4">Class 4</button>
          <button type="button" onclick="filterTextbookByGrade('5')" class="tb-grade-pill px-2 py-1 text-xs font-bold rounded-lg transition bg-white text-slate-700 hover:bg-slate-100" data-grade="5">Class 5</button>
          <button type="button" onclick="filterTextbookByGrade('6')" class="tb-grade-pill px-2 py-1 text-xs font-bold rounded-lg transition bg-white text-slate-700 hover:bg-slate-100" data-grade="6">Class 6</button>
          <button type="button" onclick="filterTextbookByGrade('7')" class="tb-grade-pill px-2 py-1 text-xs font-bold rounded-lg transition bg-white text-slate-700 hover:bg-slate-100" data-grade="7">Class 7</button>
          <button type="button" onclick="filterTextbookByGrade('8')" class="tb-grade-pill px-2 py-1 text-xs font-bold rounded-lg transition bg-white text-slate-700 hover:bg-slate-100" data-grade="8">Class 8</button>
          <button type="button" onclick="filterTextbookByGrade('9')" class="tb-grade-pill px-2 py-1 text-xs font-bold rounded-lg transition bg-white text-slate-700 hover:bg-slate-100" data-grade="9">Class 9</button>
          <button type="button" onclick="filterTextbookByGrade('10')" class="tb-grade-pill px-2 py-1 text-xs font-bold rounded-lg transition bg-white text-slate-700 hover:bg-slate-100" data-grade="10">Class 10</button>
        </div>

        <!-- Search Input -->
        <div class="relative w-full sm:w-60">
          <i data-lucide="search" class="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5"></i>
          <input type="text" id="tb-search-input" oninput="filterTextbooksBySearch()" placeholder="Search book or subject..." class="w-full clay-input pl-8 pr-3 py-1.5 text-xs font-medium text-slate-800" />
        </div>
      </div>

      <!-- Textbook Cards Grid (Scrollable) -->
      <div id="textbook-grid-container" class="overflow-y-auto pr-1 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5 flex-1 min-h-[360px]">
        <!-- Populated by JavaScript -->
      </div>
    </div>
  </div>
"""

html = html.replace(footer_tag, footer_tag + "\n" + modals_html)

# 6. REPLACE KPK_SYLLABUS WITH FULL 1-10 GRADES SYLLABUS
with open("scripts/kpk_syllabus_full.json", "r", encoding="utf-8") as f:
    full_syllabus_obj = json.load(f)

# Format into clean JS
syllabus_js = "    const KPK_SYLLABUS = " + json.dumps(full_syllabus_obj, indent=6, ensure_ascii=False) + ";\n"

# Find existing KPK_SYLLABUS block
kpk_syll_pattern = re.compile(r"    const KPK_SYLLABUS = \{[\s\S]*?\n    \};", re.MULTILINE)
assert kpk_syll_pattern.search(html), "KPK_SYLLABUS pattern not found"
html = kpk_syll_pattern.sub(syllabus_js.replace("\\", "\\\\"), html, count=1)

# 7. UPDATE CLOUD PULL AND PUSH TO SYNC OWNER MASTER PASSWORD AND SCHOOL EDITS
old_pull = """    async function pullCloudSchools() {
      try {
        const hasAbort = typeof AbortController !== 'undefined';
        const controller = hasAbort ? new AbortController() : null;
        const timeoutId = controller ? setTimeout(() => controller.abort(), 6000) : null;
        const fetchOptions = controller ? { signal: controller.signal } : {};
        const res = await fetch(CLOUD_SYNC_URL + "?t=" + Date.now(), fetchOptions);
        if (timeoutId) clearTimeout(timeoutId);
        if (!res.ok) return null;
        const json = await res.json();
        if (json && json.data && Array.isArray(json.data.schools)) {
          return json.data.schools;
        }
      } catch (err) {
        console.warn("Cloud pull error:", err.message);
      }
      return null;
    }

    async function pushCloudSchools(schools) {
      try {
        const hasAbort = typeof AbortController !== 'undefined';
        const controller = hasAbort ? new AbortController() : null;
        const timeoutId = controller ? setTimeout(() => controller.abort(), 8000) : null;
        const fetchOptions = {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            name: "examforge_schools_global",
            data: {
              version: Date.now(),
              schools: schools
            }
          })
        };
        if (controller) fetchOptions.signal = controller.signal;
        const res = await fetch(CLOUD_SYNC_URL, fetchOptions);
        if (timeoutId) clearTimeout(timeoutId);
        return res.ok;
      } catch (err) {
        console.warn("Cloud push error:", err.message);
        return false;
      }
    }"""

new_pull = """    async function pullCloudSchools() {
      try {
        const hasAbort = typeof AbortController !== 'undefined';
        const controller = hasAbort ? new AbortController() : null;
        const timeoutId = controller ? setTimeout(() => controller.abort(), 6000) : null;
        const fetchOptions = controller ? { signal: controller.signal } : {};
        const res = await fetch(CLOUD_SYNC_URL + "?t=" + Date.now(), fetchOptions);
        if (timeoutId) clearTimeout(timeoutId);
        if (!res.ok) return null;
        const json = await res.json();
        if (json && json.data) {
          if (json.data.owner_master_pwd) {
            localStorage.setItem("examforge_owner_master_pwd", json.data.owner_master_pwd);
          }
          if (Array.isArray(json.data.schools)) {
            return json.data.schools;
          }
        }
      } catch (err) {
        console.warn("Cloud pull error:", err.message);
      }
      return null;
    }

    async function pushCloudSchools(schools, customOwnerPwd = null) {
      try {
        const hasAbort = typeof AbortController !== 'undefined';
        const controller = hasAbort ? new AbortController() : null;
        const timeoutId = controller ? setTimeout(() => controller.abort(), 8000) : null;
        const ownerPwd = customOwnerPwd || localStorage.getItem("examforge_owner_master_pwd") || "";
        const fetchOptions = {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            name: "examforge_schools_global",
            data: {
              version: Date.now(),
              schools: schools,
              owner_master_pwd: ownerPwd
            }
          })
        };
        if (controller) fetchOptions.signal = controller.signal;
        const res = await fetch(CLOUD_SYNC_URL, fetchOptions);
        if (timeoutId) clearTimeout(timeoutId);
        return res.ok;
      } catch (err) {
        console.warn("Cloud push error:", err.message);
        return false;
      }
    }"""

assert old_pull in html, "Cloud pull/push target not found"
html = html.replace(old_pull, new_pull)

# 8. UPDATE SYNC LOGIC TO UPDATE EXISTING SCHOOLS (E.G. CHANGED PASSWORDS)
old_sync_inner = """          for (const s of cloudSchools) {
            if (!current.some(c => (c.username || "").toLowerCase() === (s.username || "").toLowerCase())) {
              current.unshift(s);
              updated = true;
            }
          }"""

new_sync_inner = """          for (const s of cloudSchools) {
            const existing = current.find(c => (c.username || "").toLowerCase() === (s.username || "").toLowerCase());
            if (!existing) {
              current.unshift(s);
              updated = true;
            } else if (existing.password !== s.password || existing.quota !== s.quota || existing.name !== s.name) {
              existing.password = s.password;
              existing.quota = s.quota;
              existing.name = s.name;
              if (s.principal) existing.principal = s.principal;
              if (s.phone) existing.phone = s.phone;
              updated = true;
            }
          }"""

assert old_sync_inner in html, "Sync inner target not found"
html = html.replace(old_sync_inner, new_sync_inner)

# 9. UPDATE isOwnerPasswordValid TO PREFER / INCLUDE CUSTOM OWNER PASSWORD
old_is_owner = """    function isOwnerPasswordValid(pwd) {
      if (!pwd) return false;
      const clean = pwd.trim().toLowerCase();
      const custom = (localStorage.getItem("examforge_owner_master_pwd") || "").trim().toLowerCase();
      return VALID_OWNER_KEYS.some(k => k.toLowerCase() === clean) || (custom && custom === clean);
    }"""

new_is_owner = """    function isOwnerPasswordValid(pwd) {
      if (!pwd) return false;
      const clean = pwd.trim();
      const custom = (localStorage.getItem("examforge_owner_master_pwd") || "").trim();
      return (custom && (clean.toLowerCase() === custom.toLowerCase() || clean === custom)) ||
             VALID_OWNER_KEYS.some(k => k.toLowerCase() === clean.toLowerCase());
    }"""

assert old_is_owner in html, "isOwnerPasswordValid target not found"
html = html.replace(old_is_owner, new_is_owner)

# 10. ADD JAVASCRIPT FUNCTIONS FOR CHANGE PASSWORD AND TEXTBOOK LIBRARY BEFORE WINDOW INITIALIZATION
js_extensions = """
    // =========================================================================
    // 8.5 CHANGE PASSWORD CONTROLLER (SCHOOL & OWNER MULTI-DEVICE SYNC)
    // =========================================================================
    function openChangePasswordModal(defaultRole = null) {
      const modal = document.getElementById("change-password-modal");
      if (!modal) return;
      
      const activeSchool = JSON.parse(sessionStorage.getItem("examforge_active_school") || "null");
      const isOwnerAuth = sessionStorage.getItem("examforge_owner_auth") === "true";
      
      let role = defaultRole;
      if (!role) {
        if (activeSchool) role = "school";
        else if (isOwnerAuth) role = "owner";
        else role = "school";
      }

      setChangePasswordRole(role);

      document.getElementById("change-pwd-error")?.classList.add("hidden");
      document.getElementById("change-pwd-success")?.classList.add("hidden");
      
      const curr = document.getElementById("change-pwd-current");
      const n = document.getElementById("change-pwd-new");
      const c = document.getElementById("change-pwd-confirm");
      if (curr) curr.value = "";
      if (n) n.value = "";
      if (c) c.value = "";

      modal.classList.remove("hidden");
      lucide.createIcons();
    }

    function closeChangePasswordModal() {
      const modal = document.getElementById("change-password-modal");
      if (modal) modal.classList.add("hidden");
    }

    function setChangePasswordRole(role) {
      const roleInput = document.getElementById("change-pwd-role");
      if (roleInput) roleInput.value = role;

      const badge = document.getElementById("change-pwd-account-badge");
      const userGroup = document.getElementById("change-pwd-school-username-group");
      const roleSelector = document.getElementById("change-pwd-role-selector");
      const btnSchool = document.getElementById("role-btn-school");
      const btnOwner = document.getElementById("role-btn-owner");

      const activeSchool = JSON.parse(sessionStorage.getItem("examforge_active_school") || "null");
      const isOwnerAuth = sessionStorage.getItem("examforge_owner_auth") === "true";

      if (role === "school") {
        if (btnSchool) btnSchool.className = "py-2 px-3 text-xs font-bold rounded-xl border border-orange-500 bg-orange-50 text-orange-800";
        if (btnOwner) btnOwner.className = "py-2 px-3 text-xs font-bold rounded-xl border border-slate-200 bg-white text-slate-700";
        if (activeSchool) {
          if (badge) badge.textContent = `School: ${activeSchool.name || activeSchool.username}`;
          if (userGroup) userGroup.classList.add("hidden");
          if (roleSelector) roleSelector.classList.add("hidden");
        } else {
          if (badge) badge.textContent = "School Account Password Change";
          if (userGroup) userGroup.classList.remove("hidden");
          if (roleSelector) roleSelector.classList.remove("hidden");
        }
      } else {
        if (btnOwner) btnOwner.className = "py-2 px-3 text-xs font-bold rounded-xl border border-orange-500 bg-orange-50 text-orange-800";
        if (btnSchool) btnSchool.className = "py-2 px-3 text-xs font-bold rounded-xl border border-slate-200 bg-white text-slate-700";
        if (badge) badge.textContent = "Owner Master Console (AliBuild)";
        if (userGroup) userGroup.classList.add("hidden");
        if (roleSelector && !isOwnerAuth && !activeSchool) roleSelector.classList.remove("hidden");
      }
    }

    async function handleChangePasswordSubmit(e) {
      e.preventDefault();
      const role = document.getElementById("change-pwd-role")?.value || "school";
      const curr = document.getElementById("change-pwd-current")?.value?.trim() || "";
      const newPwd = document.getElementById("change-pwd-new")?.value?.trim() || "";
      const confPwd = document.getElementById("change-pwd-confirm")?.value?.trim() || "";
      const errBox = document.getElementById("change-pwd-error");
      const succBox = document.getElementById("change-pwd-success");
      const submitBtn = document.getElementById("btn-submit-change-pwd");

      if (errBox) errBox.classList.add("hidden");
      if (succBox) succBox.classList.add("hidden");

      if (newPwd.length < 4) {
        if (errBox) {
          errBox.textContent = "New password must be at least 4 characters long.";
          errBox.classList.remove("hidden");
        }
        return;
      }

      if (newPwd !== confPwd) {
        if (errBox) {
          errBox.textContent = "New password and confirmation password do not match.";
          errBox.classList.remove("hidden");
        }
        return;
      }

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Saving & Syncing Everywhere...</span>`;
        lucide.createIcons();
      }

      try {
        if (role === "owner") {
          if (!isOwnerPasswordValid(curr)) {
            if (errBox) {
              errBox.textContent = "Current owner master password is incorrect.";
              errBox.classList.remove("hidden");
            }
            if (submitBtn) {
              submitBtn.disabled = false;
              submitBtn.innerHTML = `<i data-lucide="save" class="w-4 h-4"></i><span>Update Password & Sync Devices</span>`;
              lucide.createIcons();
            }
            return;
          }

          localStorage.setItem("examforge_owner_master_pwd", newPwd);
          const schools = getSchoolAccounts();
          await pushCloudSchools(schools, newPwd);

          if (succBox) {
            succBox.textContent = "Master Owner Password successfully updated! Your new password is now active across all devices.";
            succBox.classList.remove("hidden");
          }
          setTimeout(() => {
            closeChangePasswordModal();
          }, 1800);
        } else {
          let activeSchool = JSON.parse(sessionStorage.getItem("examforge_active_school") || "null");
          let username = activeSchool?.username;
          if (!username) {
            username = document.getElementById("change-pwd-username")?.value?.trim()?.toLowerCase();
          }

          if (!username) {
            if (errBox) {
              errBox.textContent = "Please enter your school username.";
              errBox.classList.remove("hidden");
            }
            if (submitBtn) {
              submitBtn.disabled = false;
              submitBtn.innerHTML = `<i data-lucide="save" class="w-4 h-4"></i><span>Update Password & Sync Devices</span>`;
              lucide.createIcons();
            }
            return;
          }

          let schools = getSchoolAccounts();
          const target = schools.find(s => (s.username || "").toLowerCase() === username.toLowerCase());

          if (!target) {
            if (errBox) {
              errBox.textContent = `School account '${username}' not found. Please verify the username.`;
              errBox.classList.remove("hidden");
            }
            if (submitBtn) {
              submitBtn.disabled = false;
              submitBtn.innerHTML = `<i data-lucide="save" class="w-4 h-4"></i><span>Update Password & Sync Devices</span>`;
              lucide.createIcons();
            }
            return;
          }

          if (target.password !== curr) {
            if (errBox) {
              errBox.textContent = "Current password is incorrect.";
              errBox.classList.remove("hidden");
            }
            if (submitBtn) {
              submitBtn.disabled = false;
              submitBtn.innerHTML = `<i data-lucide="save" class="w-4 h-4"></i><span>Update Password & Sync Devices</span>`;
              lucide.createIcons();
            }
            return;
          }

          target.password = newPwd;
          saveSchoolAccounts(schools);

          if (activeSchool && (activeSchool.username || "").toLowerCase() === username.toLowerCase()) {
            activeSchool.password = newPwd;
            sessionStorage.setItem("examforge_active_school", JSON.stringify(activeSchool));
          }

          await pushCloudSchools(schools);

          if (succBox) {
            succBox.textContent = `Password for '${target.name || username}' updated successfully and synced across all devices!`;
            succBox.classList.remove("hidden");
          }
          setTimeout(() => {
            closeChangePasswordModal();
          }, 1800);
        }
      } catch (err) {
        if (errBox) {
          errBox.textContent = "Error saving password: " + err.message;
          errBox.classList.remove("hidden");
        }
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = `<i data-lucide="save" class="w-4 h-4"></i><span>Update Password & Sync Devices</span>`;
          lucide.createIcons();
        }
      }
    }

    // =========================================================================
    // 8.6 KPK DIGITAL TEXTBOOK LIBRARY (CLASSES 1ST TO 10TH)
    // =========================================================================
    let currentTbGradeFilter = "all";
    let allKpkCatalogBooks = [];

    async function loadTextbookCatalog() {
      if (allKpkCatalogBooks.length > 0) return allKpkCatalogBooks;
      try {
        const res = await fetch("./books/kpk_textbooks_catalog.json");
        if (res.ok) {
          allKpkCatalogBooks = await res.json();
          return allKpkCatalogBooks;
        }
      } catch (e) {
        console.warn("Could not load local catalog json:", e);
      }
      return [];
    }

    async function openTextbookLibraryModal() {
      const modal = document.getElementById("textbook-library-modal");
      if (!modal) return;
      modal.classList.remove("hidden");
      await loadTextbookCatalog();
      renderTextbookLibraryGrid();
      lucide.createIcons();
    }

    function closeTextbookLibraryModal() {
      const modal = document.getElementById("textbook-library-modal");
      if (modal) modal.classList.add("hidden");
    }

    function filterTextbookByGrade(grade) {
      currentTbGradeFilter = String(grade);
      document.querySelectorAll(".tb-grade-pill").forEach(pill => {
        if (pill.getAttribute("data-grade") === String(grade)) {
          pill.className = "tb-grade-pill px-2.5 py-1 text-xs font-black rounded-lg transition bg-orange-600 text-white shadow-xs";
        } else {
          pill.className = "tb-grade-pill px-2 py-1 text-xs font-bold rounded-lg transition bg-white text-slate-700 hover:bg-slate-100";
        }
      });
      renderTextbookLibraryGrid();
    }

    function filterTextbooksBySearch() {
      renderTextbookLibraryGrid();
    }

    function renderTextbookLibraryGrid() {
      const container = document.getElementById("textbook-grid-container");
      if (!container) return;

      const q = (document.getElementById("tb-search-input")?.value || "").toLowerCase().trim();
      let filtered = allKpkCatalogBooks;

      if (currentTbGradeFilter !== "all") {
        filtered = filtered.filter(b => String(b.grade) === String(currentTbGradeFilter));
      }

      if (q) {
        filtered = filtered.filter(b => 
          (b.title || "").toLowerCase().includes(q) ||
          (b.subject || "").toLowerCase().includes(q) ||
          (b.grade && `class ${b.grade}`.includes(q))
        );
      }

      if (filtered.length === 0) {
        container.innerHTML = `
          <div class="col-span-full py-12 text-center text-slate-400">
            <i data-lucide="book-x" class="w-10 h-10 mx-auto text-slate-300 mb-2"></i>
            <p class="text-sm font-bold">No textbooks matched your filter or search query.</p>
          </div>
        `;
        lucide.createIcons();
        return;
      }

      container.innerHTML = filtered.map(b => {
        const isUrdu = b.language === "ur" || b.language === "ps";
        const pdfHref = b.pdfPath;
        return `
          <div class="clay-card-flat p-4 rounded-2xl border border-slate-200/90 bg-white hover:border-orange-300 transition space-y-3 flex flex-col justify-between shadow-xs">
            <div class="space-y-1.5">
              <div class="flex items-center justify-between">
                <span class="clay-badge-orange text-[10px] font-black px-2 py-0.5 rounded-full">Class ${b.grade}th</span>
                <span class="text-[10px] font-bold text-slate-400">${b.chapters ? b.chapters.length : 0} Units &bull; ${b.fileSizeKb} KB</span>
              </div>
              <h5 class="text-xs sm:text-sm font-black text-slate-900 ${isUrdu ? 'font-urdu text-right text-base' : ''}" dir="${isUrdu ? 'rtl' : 'ltr'}">${b.title}</h5>
              <p class="text-[11px] font-medium text-slate-500">${b.subject} &bull; Peshawar Board Official Curriculum</p>
            </div>
            
            <div class="pt-2 border-t border-slate-100 flex items-center gap-2">
              <a href="${pdfHref}" download="${b.title}.pdf" target="_blank" class="flex-1 clay-btn-secondary py-1.5 px-2 text-[11px] font-bold flex items-center justify-center space-x-1 text-slate-700 hover:text-orange-600" title="Open or Download Complete Authentic PDF">
                <i data-lucide="download" class="w-3.5 h-3.5"></i>
                <span>Download PDF</span>
              </a>
              <button onclick="selectTextbookForGeneration('${b.grade}', '${b.subject}')" class="flex-1 clay-btn-primary py-1.5 px-2 text-[11px] font-bold flex items-center justify-center space-x-1" title="Generate exam paper using this textbook">
                <i data-lucide="sparkles" class="w-3.5 h-3.5"></i>
                <span>Create Paper</span>
              </button>
            </div>
          </div>
        `;
      }).join("");

      lucide.createIcons();
    }

    function selectTextbookForGeneration(grade, subject) {
      closeTextbookLibraryModal();
      const gradeSel = document.getElementById("gen-grade");
      if (gradeSel) {
        gradeSel.value = String(grade);
        handleGradeChange();
      }
      setTimeout(() => {
        const subSel = document.getElementById("gen-subject");
        if (subSel) {
          subSel.value = subject;
          handleSubjectChange();
        }
        scrollToSection("generator");
      }, 50);
    }
"""

window_init_marker = "    // =========================================================================\n    // 10. WINDOW INITIALIZATION"
assert window_init_marker in html, "Window initialization marker not found"
html = html.replace(window_init_marker, js_extensions + "\n" + window_init_marker)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Successfully applied all features cleanly to index.html!")
