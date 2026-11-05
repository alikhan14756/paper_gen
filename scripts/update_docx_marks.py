with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

target = """          currentPaper.shorts.forEach((q, idx) => {
            docChildren.push(
              new Paragraph({
                children: [
                  new TextRun({ text: `Q${idx + 1}. `, bold: true }),
                  new TextRun({ text: q.text }),
                ],
              }),
              new Paragraph({ text: "" })
            );
          });

          // SECTION C: Long Questions (Numbering restarts from Q1! No individual marks!)
          const totalLongs = currentPaper.longs.length;
          const attemptLongs = Math.min(currentPaper.attemptLongs || 3, totalLongs);
          const leaveLongs = Math.max(0, totalLongs - attemptLongs);
          const perLongMarks = attemptLongs > 0 ? Math.round(marksC / attemptLongs) : 8;
          const choiceTextC = leaveLongs > 0 ? ` (Choice: Leave any ${leaveLongs} questions)` : "";
          docChildren.push(
            new Paragraph({ text: "" }),
            new Paragraph({
              children: [
                new TextRun({ text: `SECTION — C (Descriptive Long Questions)   [Marks: ${marksC}]`, bold: true }),
              ],
              heading: HeadingLevel.HEADING_3,
            }),
            new Paragraph({ text: `Note: Attempt any ${attemptLongs} questions out of ${totalLongs} questions${choiceTextC}. All questions carry equal marks (${perLongMarks} Marks each). Show complete derivations & steps.` }),
            new Paragraph({ text: "" })
          );

          currentPaper.longs.forEach((q, idx) => {
            docChildren.push(
              new Paragraph({
                children: [
                  new TextRun({ text: `Q${idx + 1}. `, bold: true }),
                  new TextRun({ text: q.text }),
                ],
              }),
              new Paragraph({ text: "" })
            );
          });"""

replacement = """          const marksStyleDocx = currentPaper.marksStyle || 'bisep-header-only';

          currentPaper.shorts.forEach((q, idx) => {
            const qMarks = q.marks || perShortMarks;
            const marksSuffix = marksStyleDocx === 'school-per-question' ? `   [${qMarks} Marks]` : (marksStyleDocx === 'compact-score' ? `   (${qMarks})` : '');
            docChildren.push(
              new Paragraph({
                children: [
                  new TextRun({ text: `Q${idx + 1}. `, bold: true }),
                  new TextRun({ text: q.text }),
                  ...(marksSuffix ? [new TextRun({ text: marksSuffix, bold: true })] : [])
                ],
              }),
              new Paragraph({ text: "" })
            );
          });

          // SECTION C: Long Questions
          const totalLongs = currentPaper.longs.length;
          const attemptLongs = Math.min(currentPaper.attemptLongs || 3, totalLongs);
          const leaveLongs = Math.max(0, totalLongs - attemptLongs);
          const perLongMarks = attemptLongs > 0 ? Math.round(marksC / attemptLongs) : 8;
          const choiceTextC = leaveLongs > 0 ? ` (Choice: Leave any ${leaveLongs} questions)` : "";
          docChildren.push(
            new Paragraph({ text: "" }),
            new Paragraph({
              children: [
                new TextRun({ text: `SECTION — C (Descriptive Long Questions)   [Marks: ${marksC}]`, bold: true }),
              ],
              heading: HeadingLevel.HEADING_3,
            }),
            new Paragraph({ text: `Note: Attempt any ${attemptLongs} questions out of ${totalLongs} questions${choiceTextC}. All questions carry equal marks (${perLongMarks} Marks each). Show complete derivations & steps.` }),
            new Paragraph({ text: "" })
          );

          currentPaper.longs.forEach((q, idx) => {
            const qMarks = q.marks || perLongMarks;
            const marksSuffix = marksStyleDocx === 'school-per-question' ? `   [${qMarks} Marks]` : (marksStyleDocx === 'compact-score' ? `   (${qMarks})` : '');
            docChildren.push(
              new Paragraph({
                children: [
                  new TextRun({ text: `Q${idx + 1}. `, bold: true }),
                  new TextRun({ text: q.text }),
                  ...(marksSuffix ? [new TextRun({ text: marksSuffix, bold: true })] : [])
                ],
              }),
              new Paragraph({ text: "" })
            );
          });"""

text_lf = text.replace('\r\n', '\n')
target_lf = target.replace('\r\n', '\n')
replacement_lf = replacement.replace('\r\n', '\n')

assert target_lf in text_lf, "Target not found in text"
new_text = text_lf.replace(target_lf, replacement_lf)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_text)

print("Successfully updated docx marks export!")
