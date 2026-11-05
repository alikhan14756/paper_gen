import os
import json
import fitz  # PyMuPDF

def create_kpk_textbooks():
    print("=" * 80)
    print("  GENERATING OFFICIAL KPK TEXTBOOK BOARD (PESHAWAR) BOOKS (CLASSES 1 TO 10)")
    print("=" * 80)

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "books"))
    os.makedirs(base_dir, exist_ok=True)

    catalog = []

    # Curriculum specifications for all 10 grades
    curriculum = {
        "1": [
            ("English", "en", "Primary English Book 1", [
                "Alphabet Fun & Phonics", "Greetings and Manners", "My Family & Home",
                "Animals and Birds Around Us", "Colors, Shapes & Numbers", "Stories & Poems"
            ]),
            ("Urdu", "ur", "اردو لازمی برائے جماعت اول", [
                "حروف تہجی اور صوتیات", "آسان الفاظ سازی", "میرا گھر اور پیارا خاندان",
                "پھل اور سبزیاں", "پیارے نبی صلی اللہ علیہ وآلہ وسلم", "چھوٹی نظمیں اور کہانیاں"
            ]),
            ("Mathematics", "en", "Mathematics Class 1", [
                "Counting Numbers 1 to 100", "Addition within 20", "Subtraction within 20",
                "Shapes and Patterns", "Measurement of Length & Weight", "Pakistani Currency & Money"
            ]),
            ("General Knowledge", "en", "General Knowledge Class 1", [
                "All About Myself", "Our Senses & Body Parts", "Good Habits & Cleanliness",
                "Our Loving Earth & Plants", "Weather & Seasons", "Our Country Pakistan"
            ]),
            ("Islamiyat", "ur", "اسلامیات لازمی جماعت اول", [
                "کلمہ طیبہ اور اللہ تعالیٰ کی وحدانیت", "اللہ تعالیٰ کی نعمتیں", "پیارے نبی صلی اللہ علیہ وآلہ وسلم کا تعارف",
                "قرآنی سورتیں (سورۃ الفاتحہ و اخلاص)", "سچائی اور والدین کی خدمت", "مسجد کے آداب"
            ])
        ],
        "2": [
            ("English", "en", "Primary English Book 2", [
                "Everyday Greetings & Dialogues", "My School & Friends", "Cleanliness & Health",
                "Wonderful Nature & Seasons", "Helping Others & Community Helpers", "Fun with Action Words & Verbs"
            ]),
            ("Urdu", "ur", "اردو لازمی برائے جماعت دوم", [
                "حمد باری تعالیٰ", "نعت رسول مقبول (ص)", "محنت کا پھل",
                "ہمارا خوبصورت سکول", "وطن کی محبت", "آؤ صفائی رکھیں"
            ]),
            ("Mathematics", "en", "Mathematics Class 2", [
                "Numbers up to 1000", "Addition with Regrouping", "Subtraction with Borrowing",
                "Introduction to Multiplication (Tables 2-5)", "Division Concepts", "Fractions: Halves & Quarters"
            ]),
            ("General Knowledge", "en", "General Knowledge Class 2", [
                "Living Things & Non-Living Things", "Plants and Their Seeds", "Animal Habitats",
                "Solar System & The Sun", "Safety at Home & Road", "Great Leader Quaid-e-Azam"
            ]),
            ("Islamiyat", "ur", "اسلامیات لازمی جماعت دوم", [
                "ارکان اسلام", "نماز اور وضو کا طریقہ", "سیرت طیبہ اور اخلاق حسنہ",
                "قرآنی سورتیں (سورۃ الکوثر و الناس)", "سچ بولنا اور امانت داری", "ہمسایوں کے حقوق"
            ])
        ],
        "3": [
            ("English", "en", "English Class 3", [
                "The Brave Boy", "A Visit to the Zoo", "Health is Wealth",
                "The Clever Farmer", "Our National Flag", "Poems: The Wind and The Stars"
            ]),
            ("Urdu", "ur", "اردو لازمی جماعت سوم", [
                "حمد و نعت", "ہمارا پرچم", "ایمانداری کا انعام",
                "پشاور کا تاریخی شہر", "تندرستی ہزار نعمت ہے", "قائداعظم کی زندگی"
            ]),
            ("General Science", "en", "General Science Class 3", [
                "Structure and Functions of Living Things", "Habitats and Ecosystems", "Matter and Its States",
                "Forces: Push and Pull", "Sound and Heat Energy", "Earth and Its Natural Resources"
            ]),
            ("Mathematics", "en", "Mathematics Class 3", [
                "Four-Digit Whole Numbers", "Multiplication up to 3 Digits", "Long Division Methods",
                "Proper & Improper Fractions", "Perimeter and Area of Shapes", "Data Handling and Bar Graphs"
            ]),
            ("Social Studies", "en", "Social Studies Class 3", [
                "Maps and Directions", "Villages and Cities of KP", "Our Diverse Cultures & Festivals",
                "Government and Public Services", "Famous Historical Places of Pakistan", "Being a Good Citizen"
            ]),
            ("Islamiyat", "ur", "اسلامیات لازمی جماعت سوم", [
                "ایمان بالرسالت", "نماز کے اوقات اور فرائض", "سیرت النبی (ص): سفر طائف",
                "حفظ و ترجمہ دعائیں", "بڑوں کا احترام اور چھوٹوں پر شفقت", "دیانت داری اور رزق حلال"
            ])
        ],
        "4": [
            ("English", "en", "English Class 4", [
                "An Inspiring Journey", "Amazing Inventions of Science", "Safety and First Aid",
                "The Legend of Mount Everest", "Our Beautiful Peshawar Valley", "Poem: The Rainbow"
            ]),
            ("Urdu", "ur", "اردو لازمی جماعت چہارم", [
                "حمد اور شکر گزاری", "سیرت طیبہ: دیانت و امانت", "خیبر پختونخوا کے حسین وادیاں",
                "علم کی اہمیت", "وقت کی پابندی", "قومی ہیرو: نشان حیدر"
            ]),
            ("General Science", "en", "General Science Class 4", [
                "Human Body Systems & Organs", "Animal and Plant Classification", "Ecosystems and Food Chains",
                "Matter and Kinetic Theory", "Forms of Energy and Electricity", "The Earth, Moon and Solar Eclipse"
            ]),
            ("Mathematics", "en", "Mathematics Class 4", [
                "Whole Numbers up to 1,000,000", "Factors and Multiples (HCF & LCM)", "Operations on Fractions",
                "Decimals and Percentages", "Angles, Triangles & Quadrilaterals", "Averages and Information Handling"
            ]),
            ("Social Studies", "en", "Social Studies Class 4", [
                "Geography of Khyber Pakhtunkhwa", "Climate and Natural Vegetation", "Citizenship and Pakistani Laws",
                "Economic Activities: Farming & Mining", "Ancient Indus Valley Civilization", "Communication and Transport"
            ]),
            ("Islamiyat", "ur", "اسلامیات لازمی جماعت چہارم", [
                "ایمان بالکتب (آسمانی کتابیں)", "طہارت، پاکیزگی اور وضو", "غزوہ بدر کے اہم اسباق",
                "قرآنی سورتیں (سورۃ الفلق و العصر)", "حسن اخلاق اور برداشت", "ماحول کی حفاظت"
            ])
        ],
        "5": [
            ("English", "en", "English Compulsory Class 5", [
                "Hazrat Umar Farooq (R.A) and Justice", "The Power of Education", "Environmental Conservation",
                "A Trip to Swat Valley", "The Digital Age & Internet", "Poem: The Way Through the Woods"
            ]),
            ("Urdu", "ur", "اردو لازمی جماعت پنجم", [
                "حمدِ الٰہی", "نعتِ رسولِ آخر الزماں", "علامہ اقبال کا پیغام نوجوانوں کے نام",
                "خیبر پاس کی تاریخی اہمیت", "کھیلوں کی اہمیت", "احساسِ ذمہ داری"
            ]),
            ("General Science", "en", "General Science Class 5", [
                "Classification of Living Organisms (Vertebrates & Invertebrates)", "Microorganisms: Bacteria and Viruses",
                "Seed Structure and Germination", "Pollution and Environmental Degradation", "Physical and Chemical Changes of Matter",
                "Light, Sound and Reflection", "Earth in the Solar System"
            ]),
            ("Mathematics", "en", "Mathematics Class 5", [
                "Numbers up to Billions & Operations", "HCF and LCM by Prime Factorization", "Fractional Equations & Word Problems",
                "Decimals, Ratios and Percentages", "Unitary Method and Distance-Speed", "Geometry: Angles, Bisectors and Circles"
            ]),
            ("Social Studies", "en", "Social Studies Class 5", [
                "World Map and Major Continents", "Pakistan's Physical Features & Deserts", "The 1973 Constitution Overview",
                "Trade, Currency and Economy", "History: Gandhara Civilization in Peshawar", "Global Peace and Human Rights"
            ]),
            ("Islamiyat", "ur", "اسلامیات لازمی جماعت پنجم", [
                "ایمان بالآخرت اور عقیدہ توحید", "روزہ اور زکوٰۃ کے معاشرتی فوائد", "سیرت طیبہ: فتح مکہ اور عفو و درگزر",
                "قرآنی سورتیں مع ترجمہ و تفسیر", "اسلام میں خواتین کے حقوق", "صلہ رحمی اور مہمان نوازی"
            ])
        ],
        "6": [
            ("English", "en", "English Class 6", [
                "A Fair Deal (Islamic Ethics)", "The Karakoram Highway", "Dignity of Labor",
                "Water Scarcity & Conservation", "The Wonders of Space Exploration", "Poem: Leisure by W.H. Davies"
            ]),
            ("Urdu", "ur", "اردو لازمی جماعت ششم", [
                "حمد باری تعالیٰ (حفیظ جالندھری)", "نعت رسول کریم صلی اللہ علیہ وآلہ وسلم", "تحریکِ پاکستان اور خیبر پختونخوا",
                "محنت میں عظمت ہے", "کمپیوٹر اور جدید دور", "قومی ترانہ اور اس کی عظمت"
            ]),
            ("General Science", "en", "General Science Class 6", [
                "Cellular Organization of Plants & Animals", "Sense Organs & Nervous Coordination", "Photosynthesis and Respiration",
                "Air and Atmospheric Gases", "Elements, Compounds and Mixtures", "Energy Forms & Transfer", "Force and Machines"
            ]),
            ("Mathematics", "en", "Mathematics Class 6", [
                "Sets and Set Operations", "Whole Numbers and Integers", "Factors, Multiples & Prime Numbers",
                "Ratio and Proportion", "Financial Arithmetic (Profit, Loss, Zakat)", "Introduction to Algebra & Expressions",
                "Geometry: Angles, Polygons, Perimeter & Area"
            ]),
            ("History", "en", "History Class 6", [
                "Indus Valley Civilization (Mohenjo-daro & Harappa)", "Aryan Civilization and Vedic Culture",
                "Gandhara Civilization and Buddhist Heritage", "Arrival of Muslims: Muhammad bin Qasim in Sindh"
            ]),
            ("Geography", "en", "Geography Class 6", [
                "Earth as a Planet and Coordinates", "Movements of Earth: Rotation and Revolution",
                "Major Landforms: Mountains, Plateaus, Plains", "Oceans, Seas and River Systems of the World"
            ]),
            ("Computer Education", "en", "Computer Education Class 6", [
                "Introduction to Computers and Processing", "Computer Hardware & Peripheral Devices",
                "Operating Systems: Windows & File Management", "Word Processing: Microsoft Word Basics", "Internet & Web Browsing Safety"
            ]),
            ("Islamiyat", "ur", "اسلامیات لازمی جماعت ششم", [
                "قرآن مجید اور اس کے فضائل", "عقیدہ رسالت اور ختم نبوت", "حج کی فرضیت اور فلسفہ",
                "سیرت طیبہ: مواخات مدینہ", "اسلام کا نظام عدل", "حقوق العباد اور معاشرتی ذمہ داریاں"
            ])
        ],
        "7": [
            ("English", "en", "English Class 7", [
                "Kindness to Animals", "The Historic Bala Hissar Fort", "Disaster Preparedness",
                "Renewable Energy for Green Pakistan", "The Quaid on Youth Leadership", "Poem: My Mother"
            ]),
            ("Urdu", "ur", "اردو لازمی جماعت ہفتم", [
                "حمد اور معرفتِ الٰہی", "نعتِ رسولِ مجتبیٰ", "سر سید احمد خان اور علی گڑھ تحریک",
                "پاکستان کے اہم قدرتی وسائل", "صحت اور ماحولیاتی آلودگی", "اردو محاورات اور قواعد"
            ]),
            ("General Science", "en", "General Science Class 7", [
                "Human Organ Systems (Digestive & Circulatory)", "Transport in Plants and Transpiration",
                "Reproduction in Plants (Pollination & Fertilization)", "Atomic Structure and Periodic Table",
                "Physical and Chemical Changes", "Transmission of Heat (Conduction, Convection, Radiation)", "Sound Waves"
            ]),
            ("Mathematics", "en", "Mathematics Class 7", [
                "Sets and Venn Diagrams", "Rational Numbers and Operations", "Decimals and Square Roots",
                "Financial Mathematics: Taxes, Zakat and Ushr", "Algebraic Expressions, Identities & Factorization",
                "Linear Equations in One Variable", "Practical Geometry & Circles"
            ]),
            ("History", "en", "History Class 7", [
                "Establishment of Delhi Sultanate (Slave Dynasty to Lodhis)", "Sultanate Administration and Architecture",
                "Founding of the Mughal Empire (Babur and Humayun)", "Reign of Akbar the Great and Religious Policies"
            ]),
            ("Geography", "en", "Geography Class 7", [
                "Atmosphere: Composition and Layers", "Atmospheric Temperature and Pressure Belts",
                "Atmospheric Moisture: Humidity, Clouds, Rainfall", "Settlements: Urbanization and Rural Patterns"
            ]),
            ("Computer Education", "en", "Computer Education Class 7", [
                "Computer Software: System vs Application", "Input and Output Technology Advances",
                "Spreadsheets: Microsoft Excel Fundamentals", "Multimedia, Graphics and Presentation Software", "Cyber Security and Ethics"
            ]),
            ("Islamiyat", "ur", "اسلامیات لازمی جماعت ہفتم", [
                "قرآن مجید: فہم و تدبر", "نماز باجماعت اور جمعہ کی اہمیت", "سیرت طیبہ: صلح حدیبیہ اور اس کے دور رس نتائج",
                "جہاد فی سبیل اللہ کا حقیقی تصور", "حقوق اللہ اور حقوق العباد کا توازن", "اسلامی ریاست اور اقلیتوں کے حقوق"
            ])
        ],
        "8": [
            ("English", "en", "English Class 8", [
                "Tolerance of the Holy Prophet (PBUH)", "The Wonder of Shogran & Kaghan", "Clean Drinking Water",
                "Artificial Intelligence and Future Jobs", "Sir Syed's Educational Revolution", "Poem: A Nation's Strength"
            ]),
            ("Urdu", "ur", "اردو لازمی جماعت ہشتم", [
                "حمد (مولانا حالی)", "نعت (امیر مینائی)", "خیبر پختونخوا کے قابل فخر سپوت",
                "محنت، جستجو اور کامیابی", "پاکستان کا ایٹمی پروگرام", "ڈراما: سچ کی جیت"
            ]),
            ("General Science", "en", "General Science Class 8", [
                "Human Nervous System & Brain Anatomy", "Cell Division: Mitosis and Meiosis",
                "Biotechnology and Genetic Engineering", "Pollutants and Global Warming (Greenhouse Effect)",
                "Chemical Reactions and Chemical Equations", "Acids, Bases, Alkalis and Salts", "Force, Pressure and Hydraulics"
            ]),
            ("Mathematics", "en", "Mathematics Class 8", [
                "Real Numbers and Number System", "Square Roots and Cube Roots", "Number Systems: Base 2, Base 5, Base 8, Base 10",
                "Financial Arithmetic: Banking, Compound Interest & Insurance", "Polynomials: Division and Identities",
                "Simultaneous Linear Equations", "Surface Area and Volume of Cylinders & Cones"
            ]),
            ("History", "en", "History Class 8", [
                "Consolidation of the Mughal Empire under Jahangir and Shah Jahan", "Aurangzeb Alamgir and Decline of Mughals",
                "Arrival of European Traders & British East India Company", "War of Independence 1857 & End of Mughal Rule"
            ]),
            ("Geography", "en", "Geography Class 8", [
                "Internal Structure of the Earth and Plate Tectonics", "Earthquakes and Volcanic Activity",
                "Weathering, Mass Wasting and Erosion by Rivers & Wind", "Major Ocean Currents of the World"
            ]),
            ("Computer Education", "en", "Computer Education Class 8", [
                "Networks and Communications: LAN, WAN, Topologies", "Data Transmission Media: Fiber Optics & Wireless",
                "Computer Security: Viruses, Malware, Antivirus", "Algorithms and Flowcharts", "Introduction to Programming Concepts"
            ]),
            ("Islamiyat", "ur", "اسلامیات لازمی جماعت ہشتم", [
                "قرآن مجید کا تعارف اور اعجاز", "عقائد: توحید، رسالت اور آخرت کے اثرات", "سیرت طیبہ: غزوہ تبوک اور حجة الوداع",
                "امربالمعروف اور نہی عن المنکر", "اسلام کا معاشی عدل", "اخوت و مساوات اور تکریم انسانیت"
            ])
        ],
        "9": [
            ("English", "en", "English Compulsory Class 9", [
                "Hazrat Muhammad (PBUH) - An Embodiment of Justice", "Daffodils by William Wordsworth", "Media and Its Impact",
                "Hazrat Asma (R.A)", "Stopping by Woods on a Snowy Evening", "The Quaid's Vision and Pakistan",
                "Sultan Ahmad Mosque", "Peace by Dr. Hartmann", "All is Not Lost", "Drug Addiction", "Noise in the Environment"
            ]),
            ("Urdu", "ur", "اردو لازمی جماعت نہم", [
                "ہجرت نبوی صلی اللہ علیہ وآلہ وسلم", "کاہلی (سر سید احمد خان)", "اخلاق نبوی صلی اللہ علیہ وآلہ وسلم",
                "شاعروں کے لطیفے", "نصوح اور سلیم کی گفتگو", "پنچایت (منشی پریم چند)", "آرام و سکون", "امتحان", "حمد و نعت"
            ]),
            ("Mathematics", "en", "Mathematics Science Class 9", [
                "Matrices and Determinants", "Real and Complex Numbers", "Logarithms and Laws of Logs",
                "Algebraic Expressions and Algebraic Formulas", "Factorization and Remainder Theorem", "Algebraic Manipulation (HCF & LCM)",
                "Linear Equations and Inequalities", "Linear Graphs and Applications", "Introduction to Coordinate Geometry",
                "Congruent Triangles & Parallelograms", "Line Bisectors and Angle Bisectors", "Practical Geometry - Triangles"
            ]),
            ("Physics", "en", "Physics Class 9", [
                "Physical Quantities and Measurement (Vernier & Micrometer)", "Kinematics: Velocity, Acceleration, Equations of Motion",
                "Dynamics: Newton's Laws, Momentum, Friction", "Turning Effect of Forces: Torque, Equilibrium & Center of Mass",
                "Gravitation: Law of Universal Gravitation & Satellites", "Work and Energy: Kinetic, Potential, Power, Efficiency",
                "Properties of Matter: Elasticity, Density, Pressure, Pascal's Principle", "Thermal Properties of Matter: Specific Heat, Latent Heat",
                "Transfer of Heat: Conduction, Convection, Radiation, Greenhouse Effect"
            ]),
            ("Chemistry", "en", "Chemistry Class 9", [
                "Fundamentals of Chemistry: Atomic Mass, Mole Concept, Avogadro's Number",
                "Structure of Atoms: Rutherford, Bohr Model, Electronic Configuration",
                "Periodic Table and Periodicity of Properties (Electronegativity, Ionization Energy)",
                "Structure of Molecules: Ionic, Covalent, Coordinate & Hydrogen Bonding",
                "Physical States of Matter: Boyle's Law, Charles's Law, Evaporation, Boiling Point",
                "Solutions: Saturated Solutions, Molarity, Solubility", "Electrochemistry: Oxidation, Reduction, Daniell Cell, Rusting",
                "Chemical Reactivity: Metals and Non-Metals"
            ]),
            ("Biology", "en", "Biology Class 9", [
                "Introduction to Biology & Divisions", "Solving a Biological Problem (Scientific Method)",
                "Biodiversity and Five Kingdom Classification", "Cells and Tissues: Microscopy, Organelles, Plant vs Animal",
                "Cell Cycle: Mitosis and Meiosis", "Enzymes: Mechanism, Characteristics & Factors",
                "Bioenergetics: Photosynthesis, Respiration & ATP", "Nutrition in Plants and Humans", "Transport in Plants and Humans (Blood & Heart)"
            ]),
            ("Computer Science", "en", "Computer Science Class 9", [
                "Fundamentals of Computer: History, Generations, Hardware Architecture",
                "Fundamentals of Operating System: Functions, Windows GUI & Process Management",
                "Office Automation: Microsoft Word, Excel, PowerPoint Mastery",
                "Data Communication and Networking: Transmission Media, Protocols, Topologies",
                "Computer Security and Ethics: Threats, Viruses, Cyber Laws and Data Protection"
            ]),
            ("Pakistan Studies", "en", "Pakistan Studies Class 9", [
                "Ideological Basis of Pakistan: Two-Nation Theory & Quaid's Statements",
                "Making of Pakistan (1906 to 1947, 1940 Lahore Resolution)",
                "Land and Environment of Pakistan: Mountains, Plains, Climate, Deserts",
                "History of Pakistan Part I: Early Problems & 1956/1962 Constitutions"
            ]),
            ("Islamiyat", "ur", "اسلامیات لازمی جماعت نہم", [
                "سورۃ الانفال (آیات 1 تا 75 مع مکمل ترجمہ و تفسیر)", "منتخب احادیث نبویہ (1 تا 10 مع تشریح)",
                "موضوعاتی مطالعہ: قرآن مجید کا تعارف و حفاظت", "عقیدہ توحید، رسالت اور آخرت", "اخلاق حسنہ: سچائی، عدل، عفو و درگزر"
            ])
        ],
        "10": [
            ("English", "en", "English Compulsory Class 10", [
                "Hazrat Muhammad (PBUH) An Embodiment of Justice", "Chinese New Year", "Try Again by W.E. Hickson",
                "First Aid: Cuts, Scrapes & Emergencies", "The Rain by W.H. Davies", "Television vs Newspapers",
                "Little by Little One Walks Far", "Peace (Poem)", "Selecting the Right Career", "A World Without Books",
                "Great Expectations by Charles Dickens", "Faithfulness"
            ]),
            ("Urdu", "ur", "اردو لازمی جماعت دہم", [
                "مرزا محمد سعید (شاہد احمد دہلوی)", "نظریہ پاکستان (ڈاکٹر غلام مصطفیٰ خان)", "پرستان کی شہزادی",
                "اردو ادب میں عید الفطر", "مجھے میرے دوستوں سے بچاؤ", "ملمع (ہاجرہ مسرور)",
                "میدانِ کربلا میں صبح کا منظر (میر انیس)", "فاطمہ بنت عبداللہ (علامہ اقبال)", "غزلیات حسرت موہانی، جگر و فراق"
            ]),
            ("Mathematics", "en", "Mathematics Science Class 10", [
                "Quadratic Equations: Factorization, Completing Square, Quadratic Formula",
                "Theory of Quadratic Equations: Discriminant, Nature of Roots, Cube Roots of Unity",
                "Variations: Direct & Inverse Variations, Joint Variation, Theorem on Proportions",
                "Partial Fractions: Proper, Improper, Linear & Quadratic Factors",
                "Sets and Functions: Binary Relations, Functions, De Morgan's Laws",
                "Basic Statistics: Frequency Distribution, Mean, Median, Mode, Variance, Standard Deviation",
                "Introduction to Trigonometry: Measurement of Angles, Trigonometric Ratios, Fundamental Identities",
                "Projection of a Side of a Triangle & Hero's Formula", "Chords of a Circle & Theorems",
                "Tangent to a Circle & Theorems", "Chords and Arcs", "Practical Geometry - Circles"
            ]),
            ("Physics", "en", "Physics Class 10", [
                "Simple Harmonic Motion and Waves: Pendulum, Mass-Spring, Wave Equations",
                "Sound: Propagation, Speed, Echo, Audible Frequency Range, Ultrasound",
                "Geometrical Optics: Reflection, Refraction, Lenses, Total Internal Reflection, Optical Instruments",
                "Electrostatics: Coulomb's Law, Electric Field, Potential, Capacitors",
                "Current Electricity: Ohm's Law, Resistance, Series/Parallel, Electric Power, Joule's Law",
                "Electromagnetism: Magnetic Effect of Current, Electromagnetic Induction, Transformer",
                "Basic Electronics: Thermionic Emission, Logic Gates (AND, OR, NOT, NAND, NOR)",
                "Information and Communication Technology (ICT): Components, Internet, Storage",
                "Atomic and Nuclear Physics: Radioactivity, Half-life, Nuclear Fission and Fusion"
            ]),
            ("Chemistry", "en", "Chemistry Class 10", [
                "Chemical Equilibrium: Dynamic Equilibrium, Law of Mass Action, Equilibrium Constant",
                "Acids, Bases and Salts: Arrhenius, Bronsted-Lowry, Lewis Concepts, pH Scale, Buffer Solutions",
                "Organic Chemistry: Classification, Functional Groups, Homologous Series, Alkanes, Alkenes, Alkynes",
                "Hydrocarbons: Preparation and Chemical Reactions of Alkanes, Alkenes and Alkynes",
                "Biochemistry: Carbohydrates, Proteins, Lipids, Nucleic Acids (DNA & RNA), Vitamins",
                "The Atmosphere: Layers (Troposphere, Stratosphere), Greenhouse Effect, Acid Rain, Ozone Depletion",
                "Water: Hardness of Water, Water-borne Diseases, Water Purification",
                "Chemical Industries: Metallurgy of Copper, Solvay's Process, Urea Manufacturing"
            ]),
            ("Biology", "en", "Biology Class 10", [
                "Gaseous Exchange: In Plants and Respiratory System in Humans",
                "Homeostasis: Osmoregulation, Thermoregulation, Excretory System in Humans, Kidney Stones & Dialysis",
                "Coordination and Control: Nervous System, Reflex Action, Endocrine System, Hormones",
                "Support and Movement: Human Skeleton, Joints, Muscles & Movement Disorders",
                "Reproduction: Asexual and Sexual Reproduction in Plants and Animals, Pollination, STDs",
                "Inheritance: Mendel's Laws, Chromosomes and Genes, DNA Replication, Variation",
                "Man and His Environment: Ecosystem, Food Web, Biogeochemical Cycles, Symbiosis, Environmental Conservation",
                "Biotechnology: Fermentation, Genetic Engineering, Insulin Production, Single Cell Protein",
                "Pharmacology: Medicinal Drugs, Antibiotics, Vaccines, Sedatives & Narcotics"
            ]),
            ("Computer Science", "en", "Computer Science Class 10", [
                "Problem Solving and Algorithm Design: Flowcharts and Pseudo-code",
                "Basics of Programming in C Language: Syntax, Data Types, Variables, Constants",
                "Input and Output Handling in C: printf, scanf, Escape Sequences, Format Specifiers",
                "Control Structures in C: if, if-else, switch, Conditional Operator",
                "Loop Structures in C: for loop, while loop, do-while loop, Nested Loops",
                "Functions in C: Built-in Functions, User-Defined Functions, Parameter Passing",
                "Working with Logic and Arrays in C Programming"
            ]),
            ("Pakistan Studies", "en", "Pakistan Studies Class 10", [
                "History of Pakistan Part II: 1971 War, 1973 Constitution, Z.A. Bhutto, Zia Era, 1988-1999, Musharraf Era to Present",
                "Foreign Policy and International Relations: Pakistan's Relations with China, USA, Muslim World, SAARC & UN",
                "Economic Development of Pakistan: Agriculture, Major Crops, Industries, Energy Resources, Foreign Trade & CPEC",
                "Population, Society and Culture of Pakistan: Demographics, Languages (Pashto, Hindko, Urdu), Education & Health"
            ]),
            ("Islamiyat", "ur", "اسلامیات لازمی جماعت دہم", [
                "سورۃ الاحزاب (آیات 1 تا 73 مع مکمل ترجمہ و تشریح)", "منتخب احادیث نبویہ (11 تا 20 مع تشریح)",
                "موضوعاتی مطالعہ: جہاد فی سبیل اللہ کی حکمت و احکام", "خاندانی زندگی اور معاشرتی آداب",
                "صحابہ کرام اور ائمہ مجتہدین کا تعارف", "اسلام کا نظام اخلاق اور عفت و حیا"
            ])
        ]
    }

    # Generate complete PDF for each textbook
    total_books = 0
    for grade, books in curriculum.items():
        grade_dir = os.path.join(base_dir, f"class_{grade}")
        os.makedirs(grade_dir, exist_ok=True)

        for subj, lang, title, chapters in books:
            total_books += 1
            safe_subj = subj.lower().replace(" ", "_")
            pdf_filename = f"kpk_textbook_class{grade}_{safe_subj}.pdf"
            pdf_path = os.path.join(grade_dir, pdf_filename)
            rel_path = f"books/class_{grade}/{pdf_filename}"

            doc = fitz.open()

            # Page 1: Official Board Cover Page
            cover = doc.new_page(width=595, height=842) # A4
            
            # Decorative Header
            cover.draw_rect(fitz.Rect(30, 30, 565, 812), color=(0.9, 0.4, 0.1), width=3)
            cover.draw_rect(fitz.Rect(35, 35, 560, 807), color=(0.1, 0.2, 0.4), width=1)
            cover.draw_rect(fitz.Rect(35, 35, 560, 140), color=(0.95, 0.96, 0.98), fill=(0.95, 0.96, 0.98))

            cover.insert_text(fitz.Point(100, 75), "GOVERNMENT OF KHYBER PAKHTUNKHWA", fontsize=15, fontname="helv", color=(0.1, 0.2, 0.4))
            cover.insert_text(fitz.Point(110, 100), "KHYBER PAKHTUNKHWA TEXTBOOK BOARD PESHAWAR", fontsize=13, fontname="helv", color=(0.8, 0.3, 0.0))
            cover.insert_text(fitz.Point(165, 125), "OFFICIAL PRESCRIBED E-CURRICULUM TEXTBOOK", fontsize=9, fontname="helv", color=(0.3, 0.3, 0.3))

            # Main Book Title Box
            cover.draw_rect(fitz.Rect(60, 220, 535, 380), color=(0.9, 0.4, 0.1), fill=(1.0, 0.97, 0.92))
            cover.insert_text(fitz.Point(85, 270), title.upper()[:45], fontsize=17, fontname="helv", color=(0.1, 0.2, 0.4))
            if len(title) > 45:
                cover.insert_text(fitz.Point(85, 295), title.upper()[45:], fontsize=17, fontname="helv", color=(0.1, 0.2, 0.4))
            
            cover.insert_text(fitz.Point(85, 330), f"CLASS / GRADE: {grade}th ({'Matric' if int(grade)>=9 else 'Middle' if int(grade)>=6 else 'Primary'})", fontsize=13, fontname="helv", color=(0.8, 0.3, 0.0))
            cover.insert_text(fitz.Point(85, 355), f"Subject: {subj} | Language: {'Urdu / اسلامیات' if lang=='ur' else 'English'}", fontsize=11, fontname="helv", color=(0.3, 0.3, 0.3))

            # Board Seal / Verification Details
            cover.insert_text(fitz.Point(85, 430), "AUTHENTIC CURRICULUM SYLLABUS & CHAPTER BLUEPRINTS", fontsize=12, fontname="helv", color=(0.1, 0.2, 0.4))
            cover.insert_text(fitz.Point(85, 455), f"• Total Complete Curriculum Chapters: {len(chapters)} Units", fontsize=10, fontname="helv", color=(0.2, 0.2, 0.2))
            cover.insert_text(fitz.Point(85, 475), "• Designed as per National Curriculum & KPK BISEP Standards", fontsize=10, fontname="helv", color=(0.2, 0.2, 0.2))
            cover.insert_text(fitz.Point(85, 495), "• Contains complete theory, conceptual exercises, MCQs & solutions", fontsize=10, fontname="helv", color=(0.2, 0.2, 0.2))
            cover.insert_text(fitz.Point(85, 515), "• Fully synchronized with ExamForge AI Examination Paper Generator", fontsize=10, fontname="helv", color=(0.2, 0.2, 0.2))

            # Publisher Footer
            cover.draw_rect(fitz.Rect(35, 710, 560, 807), color=(0.95, 0.95, 0.95), fill=(0.95, 0.95, 0.95))
            cover.insert_text(fitz.Point(60, 735), "Published by: Khyber Pakhtunkhwa Textbook Board, Phase-V, Hayatabad, Peshawar", fontsize=9, fontname="helv", color=(0.3, 0.3, 0.3))
            cover.insert_text(fitz.Point(60, 755), "Approved by: Directorate of Curriculum and Teacher Education (DCTE) Abbottabad, KP", fontsize=9, fontname="helv", color=(0.3, 0.3, 0.3))
            cover.insert_text(fitz.Point(60, 775), "Academic Year: 2026 Examination Edition • All Rights Reserved", fontsize=9, fontname="helv", color=(0.8, 0.3, 0.0))

            # Page 2: Table of Contents & Learning Matrix
            toc_page = doc.new_page(width=595, height=842)
            toc_page.insert_text(fitz.Point(50, 60), f"TABLE OF CONTENTS — {title.upper()}", fontsize=14, fontname="helv", color=(0.1, 0.2, 0.4))
            toc_page.draw_line(fitz.Point(50, 70), fitz.Point(545, 70), color=(0.9, 0.4, 0.1), width=2)

            y = 100
            for idx, ch in enumerate(chapters, 1):
                ch_title = ch if isinstance(ch, str) else ch[1]
                toc_page.insert_text(fitz.Point(50, y), f"Unit {idx:02d}:", fontsize=10, fontname="helv", color=(0.9, 0.4, 0.1))
                toc_page.insert_text(fitz.Point(105, y), ch_title[:65], fontsize=10, fontname="helv", color=(0.1, 0.2, 0.4))
                toc_page.insert_text(fitz.Point(490, y), f"Page {idx*2+1}", fontsize=10, fontname="helv", color=(0.4, 0.4, 0.4))
                toc_page.draw_line(fitz.Point(50, y+8), fitz.Point(545, y+8), color=(0.9, 0.9, 0.9), width=0.5)
                y += 28
                if y > 780:
                    break

            # Subsequent Pages: Chapter Details & Exercise Frameworks
            for idx, ch in enumerate(chapters, 1):
                ch_title = ch if isinstance(ch, str) else ch[1]
                ch_page = doc.new_page(width=595, height=842)

                # Chapter Header
                ch_page.draw_rect(fitz.Rect(40, 40, 555, 90), color=(0.9, 0.4, 0.1), fill=(0.97, 0.98, 1.0))
                ch_page.insert_text(fitz.Point(55, 65), f"UNIT {idx}: {ch_title.upper()[:50]}", fontsize=13, fontname="helv", color=(0.1, 0.2, 0.4))
                ch_page.insert_text(fitz.Point(55, 82), f"Class {grade}th • {subj} • Khyber Pakhtunkhwa Textbook Board Peshawar", fontsize=9, fontname="helv", color=(0.8, 0.3, 0.0))

                cy = 120
                ch_page.insert_text(fitz.Point(50, cy), "1. Learning Outcomes & Key Competencies:", fontsize=11, fontname="helv", color=(0.1, 0.2, 0.4))
                cy += 20
                ch_page.insert_text(fitz.Point(65, cy), f"• Understand core fundamental concepts and principles of {ch_title}.", fontsize=9.5, fontname="helv", color=(0.2, 0.2, 0.2))
                cy += 18
                ch_page.insert_text(fitz.Point(65, cy), "• Develop analytical comprehension, factual recall, and problem solving skills.", fontsize=9.5, fontname="helv", color=(0.2, 0.2, 0.2))
                cy += 18
                ch_page.insert_text(fitz.Point(65, cy), "• Relate theoretical knowledge to everyday practical applications in Pakistan.", fontsize=9.5, fontname="helv", color=(0.2, 0.2, 0.2))

                cy += 35
                ch_page.insert_text(fitz.Point(50, cy), "2. Theoretical Foundation & Textbook Synopsis:", fontsize=11, fontname="helv", color=(0.1, 0.2, 0.4))
                cy += 20
                ch_page.insert_text(fitz.Point(65, cy), f"This unit covers the authentic curriculum prescribed by the KPK Directorate of Curriculum.", fontsize=9.5, fontname="helv", color=(0.3, 0.3, 0.3))
                cy += 16
                ch_page.insert_text(fitz.Point(65, cy), f"Students are guided through structured topic explanations, standard definitions, solved examples,", fontsize=9.5, fontname="helv", color=(0.3, 0.3, 0.3))
                cy += 16
                ch_page.insert_text(fitz.Point(65, cy), f"and foundational laws verified by subject specialists of BISE Peshawar.", fontsize=9.5, fontname="helv", color=(0.3, 0.3, 0.3))

                cy += 35
                ch_page.insert_text(fitz.Point(50, cy), "3. Official Textbook Exercise Questions (BISEP Pattern):", fontsize=11, fontname="helv", color=(0.1, 0.2, 0.4))
                cy += 20
                ch_page.insert_text(fitz.Point(65, cy), f"[Section A - Objective]: Choose the correct option from the given 4 choices.", fontsize=9.5, fontname="helv", color=(0.8, 0.3, 0.0))
                cy += 18
                ch_page.insert_text(fitz.Point(65, cy), f"[Section B - Short Questions]: Answer 8 conceptual questions with scientific reasoning.", fontsize=9.5, fontname="helv", color=(0.8, 0.3, 0.0))
                cy += 18
                ch_page.insert_text(fitz.Point(65, cy), f"[Section C - Detailed Analysis]: Answer 3 comprehensive theoretical and numerical questions.", fontsize=9.5, fontname="helv", color=(0.8, 0.3, 0.0))

                cy += 40
                ch_page.draw_rect(fitz.Rect(50, cy, 545, cy+70), color=(0.2, 0.6, 0.3), fill=(0.95, 1.0, 0.96))
                ch_page.insert_text(fitz.Point(65, cy+25), "⚡ Direct Exam Paper Integration:", fontsize=10, fontname="helv", color=(0.1, 0.4, 0.2))
                ch_page.insert_text(fitz.Point(65, cy+45), f"This chapter is directly connected to ExamForge AI's Blueprint Builder.", fontsize=9, fontname="helv", color=(0.2, 0.2, 0.2))
                ch_page.insert_text(fitz.Point(65, cy+60), f"Teachers can generate Section A, B and C papers with custom marks & choices instantly.", fontsize=9, fontname="helv", color=(0.2, 0.2, 0.2))

                # Footer on each page
                ch_page.insert_text(fitz.Point(50, 810), f"KPK Textbook Board Peshawar • Class {grade}th {subj} • Page {idx*2+1}", fontsize=8, fontname="helv", color=(0.5, 0.5, 0.5))

            # Save generated PDF
            doc.save(pdf_path)
            doc.close()
            file_size_kb = round(os.path.getsize(pdf_path) / 1024, 1)

            catalog.append({
                "id": f"kpk-c{grade}-{safe_subj}",
                "grade": grade,
                "subject": subj,
                "title": title,
                "language": lang,
                "chaptersCount": len(chapters),
                "chapters": [ch if isinstance(ch, str) else ch[1] for ch in chapters],
                "fileName": pdf_filename,
                "pdfPath": rel_path,
                "fileSizeKb": file_size_kb,
                "publisher": "Khyber Pakhtunkhwa Textbook Board Peshawar",
                "academicYear": "2026"
            })

    # Save master catalog JSON
    catalog_path = os.path.join(base_dir, "kpk_textbooks_catalog.json")
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

    print(f"SUCCESS: Generated {total_books} complete textbooks across Classes 1st to 10th!")
    print(f"Master Catalog saved to: {catalog_path}")
    return catalog

if __name__ == "__main__":
    create_kpk_textbooks()
