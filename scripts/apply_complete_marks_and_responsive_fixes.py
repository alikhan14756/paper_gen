with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. UPDATE RENDERPAPERDOM TO ALWAYS RENDER EDITABLE MARKS ON EVERY QUESTION
old_render_paper = """      // Render Section A (MCQs) - No per-question marks badge
      const secAContainer = document.getElementById("sec-a-container");
      if (secAContainer) {
        secAContainer.innerHTML = currentPaper.mcqs.map((q, idx) => `
          <div class="p-2.5 rounded-lg border border-transparent hover:border-slate-200 transition group space-y-2">
            <div class="flex items-start justify-between gap-2">
              <div class="flex-1 flex items-start space-x-2">
                <span class="font-black text-slate-900 pt-0.5">Q${idx + 1}.</span>
                <div contenteditable="true" onblur="updateQuestionContent('mcq', ${idx}, this.innerText)" class="editable-text font-bold text-slate-900 flex-1 leading-relaxed">
                  ${q.text}
                </div>
              </div>
              <div class="flex items-center space-x-1 shrink-0 no-print">
                <button onclick="removeQuestion('mcq', ${idx})" title="Delete Question" class="p-1 text-slate-300 hover:text-red-600 transition">
                  <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
                </button>
              </div>
            </div>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 pl-6 text-slate-700">
              ${q.options.map((opt, optIdx) => `
                <div class="flex items-center space-x-1.5">
                  <span class="w-3.5 h-3.5 rounded-full border border-slate-500 shrink-0 inline-block"></span>
                  <span contenteditable="true" onblur="updateMcqOption(${idx}, ${optIdx}, this.innerText)" class="editable-text text-[11px] font-medium">${opt}</span>
                </div>
              `).join("")}
            </div>
          </div>
        `).join("");
      }

      // Render Section B (Short Questions)
      const secBContainer = document.getElementById("sec-b-container");
      const marksStyle = currentPaper.marksStyle || 'bisep-header-only';
      const perShortMarks = currentPaper.perShortMarks || 4;

      if (secBContainer) {
        secBContainer.innerHTML = currentPaper.shorts.map((q, idx) => {
          const qMarks = q.marks || perShortMarks;
          const marksBadgeHtml = marksStyle === 'school-per-question'
            ? `<span contenteditable="true" onblur="updateSpecificQuestionMarks('short', ${idx}, this.innerText)" class="marks-badge-editable bg-slate-100 hover:bg-orange-100 text-slate-800 text-[10px] font-black px-2 py-0.5 rounded border border-slate-300 shrink-0 ml-2" title="Click to edit marks for this question">[${qMarks} Marks]</span>`
            : (marksStyle === 'compact-score' ? `<span contenteditable="true" onblur="updateSpecificQuestionMarks('short', ${idx}, this.innerText)" class="font-bold text-slate-500 text-[11px] shrink-0 ml-2">(${qMarks})</span>` : '');

          return `
          <div class="p-2.5 rounded-lg border border-transparent hover:border-slate-200 transition group flex items-start justify-between gap-3">
            <div class="flex-1 flex items-start space-x-2">
              <span class="font-black text-slate-900 pt-0.5">Q${idx + 1}.</span>
              <div contenteditable="true" onblur="updateQuestionContent('short', ${idx}, this.innerText)" class="editable-text font-medium text-slate-900 flex-1 leading-relaxed">
                ${q.text}
              </div>
              ${marksBadgeHtml}
            </div>
            <div class="flex items-center space-x-1.5 shrink-0 no-print">
              <button onclick="removeQuestion('short', ${idx})" title="Delete Question" class="p-1 text-slate-300 hover:text-red-600 transition">
                <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
              </button>
            </div>
          </div>
        `;
        }).join("");
      }

      // Render Section C (Long Questions)
      const secCContainer = document.getElementById("sec-c-container");
      const perLongMarks = currentPaper.perLongMarks || 8;

      if (secCContainer) {
        secCContainer.innerHTML = currentPaper.longs.map((q, idx) => {
          const qMarks = q.marks || perLongMarks;
          const marksBadgeHtml = marksStyle === 'school-per-question'
            ? `<span contenteditable="true" onblur="updateSpecificQuestionMarks('long', ${idx}, this.innerText)" class="marks-badge-editable bg-slate-100 hover:bg-orange-100 text-slate-800 text-[10px] font-black px-2 py-0.5 rounded border border-slate-300 shrink-0 ml-2" title="Click to edit marks for this question">[${qMarks} Marks]</span>`
            : (marksStyle === 'compact-score' ? `<span contenteditable="true" onblur="updateSpecificQuestionMarks('long', ${idx}, this.innerText)" class="font-bold text-slate-500 text-[11px] shrink-0 ml-2">(${qMarks})</span>` : '');

          return `
          <div class="p-2.5 rounded-lg border border-transparent hover:border-slate-200 transition group flex items-start justify-between gap-3">
            <div class="flex-1 flex items-start space-x-2">
              <span class="font-black text-slate-900 pt-0.5">Q${idx + 1}.</span>
              <div contenteditable="true" onblur="updateQuestionContent('long', ${idx}, this.innerText)" class="editable-text font-medium text-slate-900 flex-1 leading-relaxed">
                ${q.text}
              </div>
              ${marksBadgeHtml}
            </div>
            <div class="flex items-center space-x-1.5 shrink-0 no-print">
              <button onclick="removeQuestion('long', ${idx})" title="Delete Question" class="p-1 text-slate-300 hover:text-red-600 transition">
                <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
              </button>
            </div>
          </div>
        `;
        }).join("");
      }"""

new_render_paper = """      // Render Section A (MCQs) - With clickable marks badge on every question
      const secAContainer = document.getElementById("sec-a-container");
      const marksStyle = currentPaper.marksStyle || 'school-per-question';
      const perShortMarks = currentPaper.perShortMarks || 4;
      const perLongMarks = currentPaper.perLongMarks || 8;

      if (secAContainer) {
        secAContainer.innerHTML = currentPaper.mcqs.map((q, idx) => {
          const qMarks = q.marks !== undefined ? q.marks : 1;
          return `
          <div class="p-2.5 rounded-lg border border-transparent hover:border-slate-200 transition group space-y-2">
            <div class="flex items-start justify-between gap-2">
              <div class="flex-1 flex items-start space-x-2">
                <span class="font-black text-slate-900 pt-0.5">Q${idx + 1}.</span>
                <div contenteditable="true" onblur="updateQuestionContent('mcq', ${idx}, this.innerText)" class="editable-text font-bold text-slate-900 flex-1 leading-relaxed">
                  ${q.text}
                </div>
                <button type="button" onclick="quickEditQuestionMarks('mcq', ${idx})" class="marks-badge-editable bg-amber-50 hover:bg-orange-100 text-orange-800 text-[10px] font-black px-2 py-0.5 rounded border border-amber-200 shrink-0 ml-1.5 shadow-2xs" title="Click to change marks for MCQ ${idx + 1}">
                  [${qMarks} M ✏️]
                </button>
              </div>
              <div class="flex items-center space-x-1 shrink-0 no-print">
                <button onclick="quickEditQuestionMarks('mcq', ${idx})" title="Edit Marks" class="p-1 text-slate-400 hover:text-orange-600 transition">
                  <i data-lucide="award" class="w-3.5 h-3.5"></i>
                </button>
                <button onclick="removeQuestion('mcq', ${idx})" title="Delete Question" class="p-1 text-slate-300 hover:text-red-600 transition">
                  <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
                </button>
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-1.5 sm:gap-2 pl-2 sm:pl-6 text-slate-700 break-words">
              ${q.options.map((opt, optIdx) => `
                <div class="flex items-center space-x-1.5">
                  <span class="w-3.5 h-3.5 rounded-full border border-slate-500 shrink-0 inline-block"></span>
                  <span contenteditable="true" onblur="updateMcqOption(${idx}, ${optIdx}, this.innerText)" class="editable-text text-[11px] font-medium">${opt}</span>
                </div>
              `).join("")}
            </div>
          </div>
        `;
        }).join("");
      }

      // Render Section B (Short Questions) - With clickable marks badge on every question
      const secBContainer = document.getElementById("sec-b-container");
      if (secBContainer) {
        secBContainer.innerHTML = currentPaper.shorts.map((q, idx) => {
          const qMarks = q.marks !== undefined ? q.marks : perShortMarks;
          return `
          <div class="p-2.5 rounded-lg border border-transparent hover:border-slate-200 transition group flex items-start justify-between gap-3">
            <div class="flex-1 flex items-start space-x-2">
              <span class="font-black text-slate-900 pt-0.5">Q${idx + 1}.</span>
              <div contenteditable="true" onblur="updateQuestionContent('short', ${idx}, this.innerText)" class="editable-text font-medium text-slate-900 flex-1 leading-relaxed">
                ${q.text}
              </div>
              <button type="button" onclick="quickEditQuestionMarks('short', ${idx})" class="marks-badge-editable bg-amber-50 hover:bg-orange-100 text-orange-900 text-[10px] font-black px-2 py-0.5 rounded border border-amber-200 shrink-0 ml-2 shadow-2xs" title="Click to change marks for Short Question ${idx + 1}">
                [${qMarks} Marks ✏️]
              </button>
            </div>
            <div class="flex items-center space-x-1.5 shrink-0 no-print">
              <button onclick="quickEditQuestionMarks('short', ${idx})" title="Edit Marks" class="p-1 text-slate-400 hover:text-orange-600 transition">
                <i data-lucide="award" class="w-3.5 h-3.5"></i>
              </button>
              <button onclick="removeQuestion('short', ${idx})" title="Delete Question" class="p-1 text-slate-300 hover:text-red-600 transition">
                <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
              </button>
            </div>
          </div>
        `;
        }).join("");
      }

      // Render Section C (Long Questions) - With clickable marks badge on every question
      const secCContainer = document.getElementById("sec-c-container");
      if (secCContainer) {
        secCContainer.innerHTML = currentPaper.longs.map((q, idx) => {
          const qMarks = q.marks !== undefined ? q.marks : perLongMarks;
          return `
          <div class="p-2.5 rounded-lg border border-transparent hover:border-slate-200 transition group flex items-start justify-between gap-3">
            <div class="flex-1 flex items-start space-x-2">
              <span class="font-black text-slate-900 pt-0.5">Q${idx + 1}.</span>
              <div contenteditable="true" onblur="updateQuestionContent('long', ${idx}, this.innerText)" class="editable-text font-medium text-slate-900 flex-1 leading-relaxed">
                ${q.text}
              </div>
              <button type="button" onclick="quickEditQuestionMarks('long', ${idx})" class="marks-badge-editable bg-amber-50 hover:bg-orange-100 text-orange-900 text-[10px] font-black px-2 py-0.5 rounded border border-amber-200 shrink-0 ml-2 shadow-2xs" title="Click to change marks for Long Question ${idx + 1}">
                [${qMarks} Marks ✏️]
              </button>
            </div>
            <div class="flex items-center space-x-1.5 shrink-0 no-print">
              <button onclick="quickEditQuestionMarks('long', ${idx})" title="Edit Marks" class="p-1 text-slate-400 hover:text-orange-600 transition">
                <i data-lucide="award" class="w-3.5 h-3.5"></i>
              </button>
              <button onclick="removeQuestion('long', ${idx})" title="Delete Question" class="p-1 text-slate-300 hover:text-red-600 transition">
                <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
              </button>
            </div>
          </div>
        `;
        }).join("");
      }"""

# Normalize line endings
html_lf = html.replace('\r\n', '\n')
old_render_lf = old_render_paper.replace('\r\n', '\n')
new_render_lf = new_render_paper.replace('\r\n', '\n')

assert old_render_lf in html_lf, "Old render paper block not found"
html = html_lf.replace(old_render_lf, new_render_lf)

# 2. UPDATE RECALCULATEMARKS FUNCTION TO COMPUTE FROM INDIVIDUAL QUESTIONS IF CUSTOMIZED
old_recalc = """    function recalculateMarks() {
      if (!currentPaper) return;

      const marksA = currentPaper.secAMarks !== undefined ? currentPaper.secAMarks : currentPaper.mcqs.length * 1;
      const marksB = currentPaper.secBMarks !== undefined ? currentPaper.secBMarks : 36;
      const marksC = currentPaper.secCMarks !== undefined ? currentPaper.secCMarks : 24;
      const marksBC = marksB + marksC;
      const grandTotal = marksA + marksBC;

      if (document.getElementById("sec-a-marks")) document.getElementById("sec-a-marks").textContent = marksA;
      if (document.getElementById("paper-head-marks-a")) document.getElementById("paper-head-marks-a").textContent = marksA;

      if (document.getElementById("sec-b-marks")) document.getElementById("sec-b-marks").textContent = marksB;
      if (document.getElementById("sec-c-marks")) document.getElementById("sec-c-marks").textContent = marksC;
      if (document.getElementById("paper-head-marks-bc")) document.getElementById("paper-head-marks-bc").textContent = marksBC;"""

new_recalc = """    function recalculateMarks() {
      if (!currentPaper) return;

      // Calculate Section A marks
      let marksA = currentPaper.secAMarks;
      if (marksA === undefined) {
        marksA = currentPaper.mcqs.reduce((sum, q) => sum + (q.marks !== undefined ? q.marks : 1), 0);
        currentPaper.secAMarks = marksA;
      }

      // Calculate Section B marks
      let marksB = currentPaper.secBMarks;
      if (marksB === undefined) {
        const attemptB = Math.min(currentPaper.attemptShorts || 9, currentPaper.shorts.length);
        const perShort = currentPaper.perShortMarks || 4;
        marksB = currentPaper.shorts.slice(0, attemptB).reduce((sum, q) => sum + (q.marks !== undefined ? q.marks : perShort), 0);
        currentPaper.secBMarks = marksB;
      }

      // Calculate Section C marks
      let marksC = currentPaper.secCMarks;
      if (marksC === undefined) {
        const attemptC = Math.min(currentPaper.attemptLongs || 3, currentPaper.longs.length);
        const perLong = currentPaper.perLongMarks || 8;
        marksC = currentPaper.longs.slice(0, attemptC).reduce((sum, q) => sum + (q.marks !== undefined ? q.marks : perLong), 0);
        currentPaper.secCMarks = marksC;
      }

      const marksBC = marksB + marksC;
      const grandTotal = marksA + marksBC;

      if (document.getElementById("sec-a-marks")) document.getElementById("sec-a-marks").textContent = marksA;
      if (document.getElementById("paper-head-marks-a")) document.getElementById("paper-head-marks-a").textContent = marksA;

      if (document.getElementById("sec-b-marks")) document.getElementById("sec-b-marks").textContent = marksB;
      if (document.getElementById("sec-c-marks")) document.getElementById("sec-c-marks").textContent = marksC;
      if (document.getElementById("paper-head-marks-bc")) document.getElementById("paper-head-marks-bc").textContent = marksBC;
      if (document.getElementById("toolbar-total-marks-label")) document.getElementById("toolbar-total-marks-label").textContent = grandTotal;"""

old_recalc_lf = old_recalc.replace('\r\n', '\n')
new_recalc_lf = new_recalc.replace('\r\n', '\n')
assert old_recalc_lf in html, "recalc block not found"
html = html.replace(old_recalc_lf, new_recalc_lf)

# 3. ADD FULL JAVASCRIPT LOGIC FOR QUICK QUESTION MARKS AND MARKS MODAL
new_controllers_code = """
    // =========================================================================
    // 8.9 INDIVIDUAL QUESTION & SECTION MARKS CONTROLLERS
    // =========================================================================
    function quickEditQuestionMarks(type, index) {
      if (!currentPaper) return;
      let list = type === 'mcq' ? currentPaper.mcqs : (type === 'short' ? currentPaper.shorts : currentPaper.longs);
      let currentVal = list[index]?.marks !== undefined
        ? list[index].marks
        : (type === 'mcq' ? 1 : (type === 'short' ? (currentPaper.perShortMarks || 4) : (currentPaper.perLongMarks || 8)));

      const label = type === 'mcq' ? `MCQ ${index + 1}` : (type === 'short' ? `Short Question ${index + 1}` : `Long Question ${index + 1}`);
      const input = prompt(`Enter new marks for ${label}:`, currentVal);
      if (input !== null) {
        const val = parseInt(input.trim(), 10);
        if (!isNaN(val) && val >= 0) {
          list[index].marks = val;

          // Recompute section totals automatically
          if (type === 'mcq') {
            currentPaper.secAMarks = currentPaper.mcqs.reduce((s, q) => s + (q.marks !== undefined ? q.marks : 1), 0);
          } else if (type === 'short') {
            const attempt = Math.min(currentPaper.attemptShorts || 9, currentPaper.shorts.length);
            currentPaper.secBMarks = currentPaper.shorts.slice(0, attempt).reduce((s, q) => s + (q.marks !== undefined ? q.marks : (currentPaper.perShortMarks || 4)), 0);
          } else if (type === 'long') {
            const attempt = Math.min(currentPaper.attemptLongs || 3, currentPaper.longs.length);
            currentPaper.secCMarks = currentPaper.longs.slice(0, attempt).reduce((s, q) => s + (q.marks !== undefined ? q.marks : (currentPaper.perLongMarks || 8)), 0);
          }

          autoSaveCurrentPaper();
          renderPaperDOM();
        }
      }
    }

    function quickEditSectionMarks(section) {
      openEditMarksModal(section);
    }

    function openEditMarksModal(focusSection = null) {
      const modal = document.getElementById("edit-marks-modal");
      if (!modal || !currentPaper) {
        if (!currentPaper) alert("Please generate an examination paper first.");
        return;
      }

      document.getElementById("modal-marks-sec-a").value = currentPaper.secAMarks !== undefined ? currentPaper.secAMarks : (currentPaper.mcqs.length * 1);
      document.getElementById("modal-marks-sec-b").value = currentPaper.secBMarks !== undefined ? currentPaper.secBMarks : 36;
      document.getElementById("modal-marks-sec-c").value = currentPaper.secCMarks !== undefined ? currentPaper.secCMarks : 24;
      document.getElementById("modal-marks-per-short").value = currentPaper.perShortMarks || 4;
      document.getElementById("modal-marks-per-long").value = currentPaper.perLongMarks || 8;
      document.getElementById("modal-marks-display-style").value = currentPaper.marksStyle || "school-per-question";

      recalcModalTotal();
      modal.classList.remove("hidden");
      lucide.createIcons();

      setTimeout(() => {
        if (focusSection === 'A') document.getElementById("modal-marks-sec-a")?.focus();
        else if (focusSection === 'B') document.getElementById("modal-marks-sec-b")?.focus();
        else if (focusSection === 'C') document.getElementById("modal-marks-sec-c")?.focus();
      }, 100);
    }

    function closeEditMarksModal() {
      const modal = document.getElementById("edit-marks-modal");
      if (modal) modal.classList.add("hidden");
    }

    function recalcModalTotal() {
      const a = parseInt(document.getElementById("modal-marks-sec-a")?.value, 10) || 0;
      const b = parseInt(document.getElementById("modal-marks-sec-b")?.value, 10) || 0;
      const c = parseInt(document.getElementById("modal-marks-sec-c")?.value, 10) || 0;
      const total = a + b + c;
      const badge = document.getElementById("modal-marks-total-badge");
      if (badge) badge.textContent = `${total} Total Marks`;
    }

    function setModalMarksPreset(preset) {
      if (preset === 50) {
        document.getElementById("modal-marks-sec-a").value = 10;
        document.getElementById("modal-marks-sec-b").value = 24;
        document.getElementById("modal-marks-sec-c").value = 16;
        document.getElementById("modal-marks-per-short").value = 3;
        document.getElementById("modal-marks-per-long").value = 8;
      } else if (preset === 100) {
        document.getElementById("modal-marks-sec-a").value = 20;
        document.getElementById("modal-marks-sec-b").value = 48;
        document.getElementById("modal-marks-sec-c").value = 32;
        document.getElementById("modal-marks-per-short").value = 4;
        document.getElementById("modal-marks-per-long").value = 8;
      } else if (preset === 25) {
        document.getElementById("modal-marks-sec-a").value = 5;
        document.getElementById("modal-marks-sec-b").value = 12;
        document.getElementById("modal-marks-sec-c").value = 8;
        document.getElementById("modal-marks-per-short").value = 2;
        document.getElementById("modal-marks-per-long").value = 4;
      } else {
        document.getElementById("modal-marks-sec-a").value = 15;
        document.getElementById("modal-marks-sec-b").value = 36;
        document.getElementById("modal-marks-sec-c").value = 24;
        document.getElementById("modal-marks-per-short").value = 4;
        document.getElementById("modal-marks-per-long").value = 8;
      }
      recalcModalTotal();
    }

    function handleApplyCustomMarksModal(e) {
      if (e && e.preventDefault) e.preventDefault();
      if (!currentPaper) return;

      const a = parseInt(document.getElementById("modal-marks-sec-a")?.value, 10) || 15;
      const b = parseInt(document.getElementById("modal-marks-sec-b")?.value, 10) || 36;
      const c = parseInt(document.getElementById("modal-marks-sec-c")?.value, 10) || 24;
      const perShort = parseInt(document.getElementById("modal-marks-per-short")?.value, 10) || 4;
      const perLong = parseInt(document.getElementById("modal-marks-per-long")?.value, 10) || 8;
      const style = document.getElementById("modal-marks-display-style")?.value || "school-per-question";

      currentPaper.secAMarks = a;
      currentPaper.secBMarks = b;
      currentPaper.secCMarks = c;
      currentPaper.perShortMarks = perShort;
      currentPaper.perLongMarks = perLong;
      currentPaper.marksStyle = style;

      // Update question models
      currentPaper.shorts.forEach(q => { q.marks = perShort; });
      currentPaper.longs.forEach(q => { q.marks = perLong; });

      closeEditMarksModal();
      autoSaveCurrentPaper();
      renderPaperDOM();
    }

    // =========================================================================
    // 8.10 MOBILE NAVIGATION MENU TOGGLE CONTROLLER
    // =========================================================================
    let mobileNavMenuOpen = false;
    function toggleMobileNavMenu() {
      mobileNavMenuOpen = !mobileNavMenuOpen;
      const drawer = document.getElementById("mobile-nav-drawer");
      const icon = document.getElementById("mobile-menu-icon");
      if (drawer) {
        if (mobileNavMenuOpen) {
          drawer.classList.remove("hidden");
          if (icon) icon.setAttribute("data-lucide", "x");
        } else {
          drawer.classList.add("hidden");
          if (icon) icon.setAttribute("data-lucide", "menu");
        }
        lucide.createIcons();
      }
    }

    function closeMobileNavMenu() {
      mobileNavMenuOpen = false;
      const drawer = document.getElementById("mobile-nav-drawer");
      const icon = document.getElementById("mobile-menu-icon");
      if (drawer) drawer.classList.add("hidden");
      if (icon) icon.setAttribute("data-lucide", "menu");
      lucide.createIcons();
    }
"""

# Insert new_controllers_code before `window.addEventListener("DOMContentLoaded"`
dom_marker = '    window.addEventListener("DOMContentLoaded", () => {'
assert dom_marker in html, "DOMContentLoaded marker not found"
html = html.replace(dom_marker, new_controllers_code + "\n" + dom_marker)

# Update updateAuthUI to also sync mobile school status & login buttons
old_auth_ui = """        if (activeModeLabel) {
          activeModeLabel.textContent = `School: ${currentUser.schoolName} (Unlimited Mode)`;
          activeModeLabel.className = "clay-badge-orange font-bold px-2.5 py-1 rounded-full text-[11px]";
        }
      } else {"""

new_auth_ui = """        if (activeModeLabel) {
          activeModeLabel.textContent = `School: ${currentUser.schoolName} (Unlimited Mode)`;
          activeModeLabel.className = "clay-badge-orange font-bold px-2.5 py-1 rounded-full text-[11px]";
        }
        const schoolStatusMob = document.getElementById("nav-school-status-mobile");
        const loginBtnMob = document.getElementById("btn-nav-login-mobile");
        const navSchoolNameMob = document.getElementById("nav-school-name-mobile");
        if (schoolStatusMob) schoolStatusMob.classList.remove("hidden");
        if (loginBtnMob) loginBtnMob.classList.add("hidden");
        if (navSchoolNameMob) navSchoolNameMob.textContent = currentUser.schoolName;
      } else {
        const schoolStatusMob = document.getElementById("nav-school-status-mobile");
        const loginBtnMob = document.getElementById("btn-nav-login-mobile");
        if (schoolStatusMob) schoolStatusMob.classList.add("hidden");
        if (loginBtnMob) loginBtnMob.classList.remove("hidden");"""

old_auth_ui_lf = old_auth_ui.replace('\r\n', '\n')
new_auth_ui_lf = new_auth_ui.replace('\r\n', '\n')
if old_auth_ui_lf in html:
    html = html.replace(old_auth_ui_lf, new_auth_ui_lf)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Applied complete marks and responsive fixes to index.html!")
