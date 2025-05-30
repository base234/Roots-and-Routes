   -- First, ensure correct context
   USE DATABASE ROOTS_ROUTES;
   USE SCHEMA PUBLIC;
   USE WAREHOUSE COMPUTE_WH;

   -- Verify current role
   -- SELECT CURRENT_ROLE();

   -- If not using roots_routes_app_role, switch to it
   -- USE ROLE roots_routes_app_role;

   -- Then try accessing the table
   SELECT COUNT(*) FROM HERITAGE_SITES;

-- =============================================
-- HERITAGE SITES DATA
-- =============================================

-- UNESCO World Heritage Sites
INSERT INTO HERITAGE_SITES (name, description, location, latitude, longitude, state, city, established_year, heritage_type, unesco_status, risk_level, health_index)
VALUES
    ('Taj Mahal', 'Iconic white marble mausoleum in Agra', 'Agra', 27.1751, 78.0421, 'Uttar Pradesh', 'Agra', 1653, 'Monument', TRUE, 'Low', 0.95),
    ('Khajuraho Temples', 'Group of Hindu and Jain temples', 'Khajuraho', 24.8510, 79.9335, 'Madhya Pradesh', 'Khajuraho', 950, 'Temple', TRUE, 'Medium', 0.85),
    ('Hampi Ruins', 'Ancient city ruins', 'Hampi', 15.3350, 76.4600, 'Karnataka', 'Hampi', 1336, 'Ruins', TRUE, 'High', 0.75),
    ('Konark Sun Temple', '13th-century Sun Temple', 'Konark', 19.8876, 86.0945, 'Odisha', 'Konark', 1250, 'Temple', TRUE, 'Medium', 0.80),
    ('Ajanta Caves', 'Ancient Buddhist cave monuments', 'Ajanta', 20.5519, 75.7033, 'Maharashtra', 'Aurangabad', 200, 'Cave', TRUE, 'Low', 0.90),
    ('Ellora Caves', 'Rock-cut cave monuments', 'Ellora', 20.0260, 75.1780, 'Maharashtra', 'Aurangabad', 600, 'Cave', TRUE, 'Low', 0.88),
    ('Mahabalipuram', 'Group of monuments', 'Mahabalipuram', 12.6168, 80.1924, 'Tamil Nadu', 'Chennai', 700, 'Temple', TRUE, 'Low', 0.92),
    ('Sanchi Stupa', 'Buddhist complex', 'Sanchi', 23.4795, 77.7396, 'Madhya Pradesh', 'Bhopal', 300, 'Monument', TRUE, 'Low', 0.87),
    ('Fatehpur Sikri', 'Mughal city', 'Fatehpur Sikri', 27.0945, 77.6679, 'Uttar Pradesh', 'Agra', 1571, 'Fort', TRUE, 'Medium', 0.82),
    ('Qutub Minar', 'Victory tower', 'Delhi', 28.5245, 77.1855, 'Delhi', 'New Delhi', 1193, 'Monument', TRUE, 'Low', 0.89),
    ('Red Fort', 'Mughal fort', 'Delhi', 28.6562, 77.2410, 'Delhi', 'New Delhi', 1648, 'Fort', TRUE, 'Low', 0.91),
    ('Chola Temples', 'Group of temples', 'Thanjavur', 10.7829, 79.1318, 'Tamil Nadu', 'Thanjavur', 1000, 'Temple', TRUE, 'Medium', 0.84),
    ('Pattadakal', 'Group of monuments', 'Pattadakal', 15.9483, 75.8167, 'Karnataka', 'Badami', 700, 'Temple', TRUE, 'Medium', 0.83),
    ('Elephanta Caves', 'Cave temples', 'Elephanta', 18.9633, 72.9315, 'Maharashtra', 'Mumbai', 500, 'Cave', TRUE, 'High', 0.78),
    ('Champaner-Pavagadh', 'Archaeological park', 'Champaner', 22.4850, 73.5378, 'Gujarat', 'Vadodara', 800, 'Fort', TRUE, 'High', 0.76),
    ('Rani Ki Vav', 'Stepwell', 'Patan', 23.8587, 72.1018, 'Gujarat', 'Patan', 1063, 'Monument', TRUE, 'Low', 0.93),
    ('Great Living Chola Temples', 'Temple complex', 'Thanjavur', 10.7829, 79.1318, 'Tamil Nadu', 'Thanjavur', 1000, 'Temple', TRUE, 'Medium', 0.85),
    ('Group of Monuments at Hampi', 'Ruins of Vijayanagara', 'Hampi', 15.3350, 76.4600, 'Karnataka', 'Hampi', 1336, 'Ruins', TRUE, 'High', 0.77),
    ('Group of Monuments at Pattadakal', 'Temple complex', 'Pattadakal', 15.9483, 75.8167, 'Karnataka', 'Badami', 700, 'Temple', TRUE, 'Medium', 0.82),
    ('Buddhist Monuments at Sanchi', 'Buddhist complex', 'Sanchi', 23.4795, 77.7396, 'Madhya Pradesh', 'Bhopal', 300, 'Monument', TRUE, 'Low', 0.88);

-- Non-UNESCO Heritage Sites
INSERT INTO HERITAGE_SITES (name, description, location, latitude, longitude, state, city, established_year, heritage_type, unesco_status, risk_level, health_index)
VALUES
    ('Golconda Fort', 'Medieval fort', 'Hyderabad', 17.3833, 78.4011, 'Telangana', 'Hyderabad', 1200, 'Fort', FALSE, 'Medium', 0.82),
    ('Charminar', 'Historic monument', 'Hyderabad', 17.3616, 78.4747, 'Telangana', 'Hyderabad', 1591, 'Monument', FALSE, 'Low', 0.88),
    ('Victoria Memorial', 'Marble building', 'Kolkata', 22.5448, 88.3426, 'West Bengal', 'Kolkata', 1921, 'Monument', FALSE, 'Low', 0.90),
    ('Howrah Bridge', 'Suspension bridge', 'Kolkata', 22.5958, 88.3436, 'West Bengal', 'Kolkata', 1943, 'Bridge', FALSE, 'Medium', 0.85),
    ('Gateway of India', 'Historic arch', 'Mumbai', 18.9217, 72.8347, 'Maharashtra', 'Mumbai', 1924, 'Monument', FALSE, 'Low', 0.89),
    ('Marine Drive', 'Coastal road', 'Mumbai', 18.9597, 72.8247, 'Maharashtra', 'Mumbai', 1920, 'Road', FALSE, 'Low', 0.92),
    ('Jantar Mantar', 'Astronomical observatory', 'Jaipur', 26.9249, 75.8247, 'Rajasthan', 'Jaipur', 1734, 'Observatory', TRUE, 'Low', 0.87),
    ('Amber Fort', 'Historic fort', 'Jaipur', 26.9855, 75.8513, 'Rajasthan', 'Jaipur', 1592, 'Fort', FALSE, 'Low', 0.91),
    ('City Palace', 'Royal palace', 'Jaipur', 26.9258, 75.8237, 'Rajasthan', 'Jaipur', 1727, 'Palace', FALSE, 'Low', 0.93),
    ('Hawa Mahal', 'Palace of winds', 'Jaipur', 26.9239, 75.8267, 'Rajasthan', 'Jaipur', 1799, 'Palace', FALSE, 'Low', 0.88),
    ('Mysore Palace', 'Royal palace of the Wadiyar dynasty', 'Mysore', 12.3052, 76.6552, 'Karnataka', 'Mysore', 1912, 'Palace', FALSE, 'Low', 0.94),
    ('Brihadeeswara Temple', 'Ancient Hindu temple', 'Thanjavur', 10.7829, 79.1318, 'Tamil Nadu', 'Thanjavur', 1010, 'Temple', TRUE, 'Low', 0.92),
    ('Meenakshi Temple', 'Historic Hindu temple', 'Madurai', 9.9197, 78.1194, 'Tamil Nadu', 'Madurai', 1190, 'Temple', FALSE, 'Low', 0.91),
    ('Sundarbans', 'Mangrove forest', 'Sundarbans', 21.9497, 89.1833, 'West Bengal', 'Kolkata', 1987, 'Forest', TRUE, 'High', 0.78),
    ('Kaziranga National Park', 'Wildlife sanctuary', 'Kaziranga', 26.5720, 93.1715, 'Assam', 'Jorhat', 1905, 'Park', TRUE, 'Medium', 0.85);

-- =============================================
-- ART FORMS DATA
-- =============================================

-- Classical Art Forms
INSERT INTO ART_FORMS (name, description, origin_state, category, risk_level, practitioners_count)
VALUES
    ('Kathakali', 'Classical dance-drama from Kerala', 'Kerala', 'Dance', 'Low', 5000),
    ('Kathak', 'Classical dance form', 'Uttar Pradesh', 'Dance', 'Low', 8000),
    ('Bharatanatyam', 'Classical dance form', 'Tamil Nadu', 'Dance', 'Low', 12000),
    ('Kuchipudi', 'Classical dance form', 'Andhra Pradesh', 'Dance', 'Medium', 6000),
    ('Odissi', 'Classical dance form', 'Odisha', 'Dance', 'Medium', 5000),
    ('Manipuri', 'Classical dance form', 'Manipur', 'Dance', 'High', 3000),
    ('Mohiniyattam', 'Classical dance form', 'Kerala', 'Dance', 'Medium', 4000),
    ('Sattriya', 'Classical dance form', 'Assam', 'Dance', 'High', 2500);

-- Folk Art Forms
INSERT INTO ART_FORMS (name, description, origin_state, category, risk_level, practitioners_count)
VALUES
    ('Madhubani', 'Folk painting from Bihar', 'Bihar', 'Painting', 'Medium', 10000),
    ('Pattachitra', 'Traditional cloth-based scroll painting', 'Odisha', 'Painting', 'High', 3000),
    ('Chhau', 'Tribal martial dance', 'West Bengal', 'Dance', 'Medium', 4000),
    ('Warli', 'Tribal art form from Maharashtra', 'Maharashtra', 'Painting', 'Low', 8000),
    ('Kalamkari', 'Hand-painted textile art', 'Andhra Pradesh', 'Textile', 'Medium', 6000),
    ('Phulkari', 'Embroidery from Punjab', 'Punjab', 'Textile', 'Low', 12000),
    ('Gond', 'Tribal painting from Madhya Pradesh', 'Madhya Pradesh', 'Painting', 'Medium', 7000),
    ('Garba', 'Folk dance', 'Gujarat', 'Dance', 'Low', 15000),
    ('Bhangra', 'Folk dance', 'Punjab', 'Dance', 'Low', 20000),
    ('Lavani', 'Folk dance', 'Maharashtra', 'Dance', 'Medium', 7000),
    ('Yakshagana', 'Traditional theatre form', 'Karnataka', 'Theatre', 'Medium', 3500),
    ('Theyyam', 'Ritual art form', 'Kerala', 'Ritual', 'High', 2000),
    ('Kalbelia', 'Folk dance', 'Rajasthan', 'Dance', 'Medium', 4500),
    ('Bihu', 'Folk dance', 'Assam', 'Dance', 'Low', 18000),
    ('Dandiya Raas', 'Folk dance', 'Gujarat', 'Dance', 'Low', 25000);

-- =============================================
-- CULTURAL EVENTS DATA
-- =============================================

-- Dance and Music Festivals
INSERT INTO CULTURAL_EVENTS (name, description, start_date, end_date, location, event_type, organizer)
VALUES
    ('Khajuraho Dance Festival', 'Annual classical dance festival', '2024-02-20', '2024-02-26', 'Khajuraho', 'Dance Festival', 'MP Tourism'),
    ('Konark Festival', 'Classical dance and music festival', '2024-12-01', '2024-12-05', 'Konark', 'Music Festival', 'Odisha Tourism'),
    ('Ellora Festival', 'Music and dance festival', '2024-12-25', '2024-12-27', 'Aurangabad', 'Music Festival', 'Maharashtra Tourism'),
    ('Mahabalipuram Dance Festival', 'Classical dance festival', '2024-01-01', '2024-01-15', 'Mahabalipuram', 'Dance Festival', 'Tamil Nadu Tourism'),
    ('Pattadakal Dance Festival', 'Classical dance festival', '2024-02-01', '2024-02-05', 'Pattadakal', 'Dance Festival', 'Karnataka Tourism'),
    ('Qutub Festival', 'Music and dance festival', '2024-11-15', '2024-11-17', 'Delhi', 'Music Festival', 'Delhi Tourism'),
    ('Elephanta Festival', 'Music and dance festival', '2024-02-15', '2024-02-17', 'Mumbai', 'Music Festival', 'Maharashtra Tourism');

-- Cultural and Heritage Festivals
INSERT INTO CULTURAL_EVENTS (name, description, start_date, end_date, location, event_type, organizer)
VALUES
    ('Hampi Utsav', 'Cultural festival at Hampi', '2024-11-03', '2024-11-05', 'Hampi', 'Cultural Festival', 'Karnataka Tourism'),
    ('Taj Mahotsav', 'Cultural festival at Agra', '2024-02-18', '2024-02-27', 'Agra', 'Cultural Festival', 'UP Tourism'),
    ('Sanchi Festival', 'Buddhist cultural festival', '2024-11-15', '2024-11-17', 'Sanchi', 'Cultural Festival', 'MP Tourism'),
    ('Fatehpur Sikri Festival', 'Mughal cultural festival', '2024-03-01', '2024-03-05', 'Fatehpur Sikri', 'Cultural Festival', 'UP Tourism'),
    ('Red Fort Festival', 'Cultural festival', '2024-12-25', '2024-12-27', 'Delhi', 'Cultural Festival', 'Delhi Tourism'),
    ('Chola Heritage Festival', 'Temple festival', '2024-01-15', '2024-01-20', 'Thanjavur', 'Cultural Festival', 'Tamil Nadu Tourism'),
    ('Champaner Heritage Festival', 'Cultural festival', '2024-03-15', '2024-03-17', 'Champaner', 'Cultural Festival', 'Gujarat Tourism'),
    ('Rani Ki Vav Festival', 'Cultural festival', '2024-04-01', '2024-04-05', 'Patan', 'Cultural Festival', 'Gujarat Tourism'),
    ('Mysore Dasara', 'Royal festival', '2024-10-15', '2024-10-24', 'Mysore', 'Cultural Festival', 'Karnataka Tourism'),
    ('Pongal Festival', 'Harvest festival', '2024-01-15', '2024-01-18', 'Madurai', 'Cultural Festival', 'Tamil Nadu Tourism'),
    ('Bihu Festival', 'Assamese new year', '2024-04-14', '2024-04-16', 'Guwahati', 'Cultural Festival', 'Assam Tourism'),
    ('Sundarbans Festival', 'Eco-tourism festival', '2024-12-20', '2024-12-22', 'Sundarbans', 'Eco Festival', 'West Bengal Tourism'),
    ('Kaziranga Festival', 'Wildlife festival', '2024-02-01', '2024-02-03', 'Kaziranga', 'Wildlife Festival', 'Assam Tourism');

-- =============================================
-- VISITOR STATISTICS DATA
-- =============================================

-- Winter 2023 Data
INSERT INTO VISITOR_STATS (site_id, visit_date, visitor_count, revenue, season)
VALUES
    (1, '2023-01-01', 5000, 250000, 'Winter'),
    (1, '2023-01-02', 4500, 225000, 'Winter'),
    (1, '2023-01-03', 4800, 240000, 'Winter'),
    (2, '2023-01-01', 2000, 100000, 'Winter'),
    (2, '2023-01-02', 1800, 90000, 'Winter'),
    (2, '2023-01-03', 2200, 110000, 'Winter'),
    (3, '2023-01-01', 1500, 75000, 'Winter'),
    (3, '2023-01-02', 1300, 65000, 'Winter'),
    (3, '2023-01-03', 1400, 70000, 'Winter'),
    (4, '2023-01-01', 1800, 90000, 'Winter'),
    (4, '2023-01-02', 1600, 80000, 'Winter'),
    (4, '2023-01-03', 1700, 85000, 'Winter'),
    (5, '2023-01-01', 2200, 110000, 'Winter'),
    (5, '2023-01-02', 2000, 100000, 'Winter'),
    (5, '2023-01-03', 2100, 105000, 'Winter');
    (6, '2023-01-01', 1693, 84650, 'Winter'),
    (6, '2023-01-02', 5707, 285350, 'Winter'),
    (6, '2023-01-03', 4309, 215450, 'Winter'),
    (7, '2023-01-01', 1675, 83750, 'Winter'),
    (7, '2023-01-02', 4254, 212700, 'Winter'),
    (7, '2023-01-03', 4355, 217750, 'Winter'),
    (8, '2023-01-01', 5261, 263050, 'Winter'),
    (8, '2023-01-02', 3523, 176150, 'Winter'),
    (8, '2023-01-03', 1811, 90550, 'Winter'),
    (9, '2023-01-01', 5938, 296900, 'Winter'),
    (9, '2023-01-02', 1953, 97650, 'Winter'),
    (9, '2023-01-03', 3769, 188450, 'Winter'),
    (10, '2023-01-01', 5080, 254000, 'Winter'),
    (10, '2023-01-02', 5248, 262400, 'Winter'),
    (10, '2023-01-03', 1900, 95000, 'Winter');

-- Spring 2023 Data
INSERT INTO VISITOR_STATS (site_id, visit_date, visitor_count, revenue, season)
VALUES
    (1, '2023-03-01', 5500, 275000, 'Spring'),
    (1, '2023-03-02', 5200, 260000, 'Spring'),
    (1, '2023-03-03', 5400, 270000, 'Spring'),
    (2, '2023-03-01', 2300, 115000, 'Spring'),
    (2, '2023-03-02', 2100, 105000, 'Spring'),
    (2, '2023-03-03', 2400, 120000, 'Spring'),
    (3, '2023-03-01', 1700, 85000, 'Spring'),
    (3, '2023-03-02', 1500, 75000, 'Spring'),
    (3, '2023-03-03', 1600, 80000, 'Spring'),
    (4, '2023-03-01', 2000, 100000, 'Spring'),
    (4, '2023-03-02', 1800, 90000, 'Spring'),
    (4, '2023-03-03', 1900, 95000, 'Spring'),
    (5, '2023-03-01', 2400, 120000, 'Spring'),
    (5, '2023-03-02', 2200, 110000, 'Spring'),
    (5, '2023-03-03', 2300, 115000, 'Spring');
    (6, '2023-03-01', 5801, 290050, 'Spring'),
    (6, '2023-03-02', 1762, 88100, 'Spring'),
    (6, '2023-03-03', 5551, 277550, 'Spring'),
    (7, '2023-03-01', 3858, 192900, 'Spring'),
    (7, '2023-03-02', 3026, 151300, 'Spring'),
    (7, '2023-03-03', 3967, 198350, 'Spring'),
    (8, '2023-03-01', 5159, 257950, 'Spring'),
    (8, '2023-03-02', 1884, 94200, 'Spring'),
    (8, '2023-03-03', 1914, 95700, 'Spring'),
    (9, '2023-03-01', 4767, 238350, 'Spring'),
    (9, '2023-03-02', 5698, 284900, 'Spring'),
    (9, '2023-03-03', 5703, 285150, 'Spring'),
    (10, '2023-03-01', 4812, 240600, 'Spring'),
    (10, '2023-03-02', 4717, 235850, 'Spring'),
    (10, '2023-03-03', 4969, 248450, 'Spring');

-- Summer 2023 Data
INSERT INTO VISITOR_STATS (site_id, visit_date, visitor_count, revenue, season)
VALUES
    (1, '2023-06-01', 4200, 210000, 'Summer'),
    (1, '2023-06-02', 4500, 225000, 'Summer'),
    (1, '2023-06-03', 4800, 240000, 'Summer'),
    (2, '2023-06-01', 2800, 140000, 'Summer'),
    (2, '2023-06-02', 3000, 150000, 'Summer'),
    (2, '2023-06-03', 3200, 160000, 'Summer'),
    (3, '2023-06-01', 1800, 90000, 'Summer'),
    (3, '2023-06-02', 2000, 100000, 'Summer'),
    (3, '2023-06-03', 2200, 110000, 'Summer'),
    (4, '2023-06-01', 2200, 110000, 'Summer'),
    (4, '2023-06-02', 2400, 120000, 'Summer'),
    (4, '2023-06-03', 2600, 130000, 'Summer'),
    (5, '2023-06-01', 2800, 140000, 'Summer'),
    (5, '2023-06-02', 3000, 150000, 'Summer'),
    (5, '2023-06-03', 3200, 160000, 'Summer');
    (6, '2023-06-01', 5857, 292850, 'Summer'),
    (6, '2023-06-02', 4025, 201250, 'Summer'),
    (6, '2023-06-03', 5082, 254100, 'Summer'),
    (7, '2023-06-01', 3333, 166650, 'Summer'),
    (7, '2023-06-02', 4687, 234350, 'Summer'),
    (7, '2023-06-03', 3579, 178950, 'Summer'),
    (8, '2023-06-01', 4349, 217450, 'Summer'),
    (8, '2023-06-02', 3822, 191100, 'Summer'),
    (8, '2023-06-03', 3319, 165950, 'Summer'),
    (9, '2023-06-01', 2591, 129550, 'Summer'),
    (9, '2023-06-02', 1533, 76650, 'Summer'),
    (9, '2023-06-03', 4349, 217450, 'Summer'),
    (10, '2023-06-01', 3470, 173500, 'Summer'),
    (10, '2023-06-02', 5672, 283600, 'Summer'),
    (10, '2023-06-03', 3322, 166100, 'Summer');

-- Monsoon 2023 Data
INSERT INTO VISITOR_STATS (site_id, visit_date, visitor_count, revenue, season)
VALUES
    (1, '2023-07-01', 3500, 175000, 'Monsoon'),
    (1, '2023-07-02', 3800, 190000, 'Monsoon'),
    (1, '2023-07-03', 4000, 200000, 'Monsoon'),
    (2, '2023-07-01', 2200, 110000, 'Monsoon'),
    (2, '2023-07-02', 2400, 120000, 'Monsoon'),
    (2, '2023-07-03', 2600, 130000, 'Monsoon'),
    (3, '2023-07-01', 1500, 75000, 'Monsoon'),
    (3, '2023-07-02', 1700, 85000, 'Monsoon'),
    (3, '2023-07-03', 1900, 95000, 'Monsoon'),
    (4, '2023-07-01', 1800, 90000, 'Monsoon'),
    (4, '2023-07-02', 2000, 100000, 'Monsoon'),
    (4, '2023-07-03', 2200, 110000, 'Monsoon'),
    (5, '2023-07-01', 2000, 100000, 'Monsoon'),
    (5, '2023-07-02', 2200, 110000, 'Monsoon'),
    (5, '2023-07-03', 2400, 120000, 'Monsoon');
    (6, '2023-07-01', 2310, 115500, 'Monsoon'),
    (7, '2023-07-01', 2486, 124300, 'Monsoon'),
    (8, '2023-07-01', 3396, 169800, 'Monsoon'),
    (9, '2023-07-01', 1796, 89800, 'Monsoon'),
    (10, '2023-07-01', 5732, 286600, 'Monsoon');

-- Autumn 2023 Data
INSERT INTO VISITOR_STATS (site_id, visit_date, visitor_count, revenue, season)
VALUES
    (1, '2023-10-01', 5200, 260000, 'Autumn'),
    (1, '2023-10-02', 5500, 275000, 'Autumn'),
    (1, '2023-10-03', 5800, 290000, 'Autumn'),
    (2, '2023-10-01', 3200, 160000, 'Autumn'),
    (2, '2023-10-02', 3500, 175000, 'Autumn'),
    (2, '2023-10-03', 3800, 190000, 'Autumn'),
    (3, '2023-10-01', 2200, 110000, 'Autumn'),
    (3, '2023-10-02', 2400, 120000, 'Autumn'),
    (3, '2023-10-03', 2600, 130000, 'Autumn'),
    (4, '2023-10-01', 2600, 130000, 'Autumn'),
    (4, '2023-10-02', 2800, 140000, 'Autumn'),
    (4, '2023-10-03', 3000, 150000, 'Autumn'),
    (5, '2023-10-01', 3000, 150000, 'Autumn'),
    (5, '2023-10-02', 3200, 160000, 'Autumn'),
    (5, '2023-10-03', 3400, 170000, 'Autumn');
    (6, '2023-10-01', 4698, 234900, 'Autumn'),
    (6, '2023-10-02', 3831, 191550, 'Autumn'),
    (6, '2023-10-03', 3727, 186350, 'Autumn'),
    (7, '2023-10-01', 4516, 225800, 'Autumn'),
    (7, '2023-10-02', 4166, 208300, 'Autumn'),
    (7, '2023-10-03', 4114, 205700, 'Autumn'),
    (8, '2023-10-01', 4393, 219650, 'Autumn'),
    (8, '2023-10-02', 4981, 249050, 'Autumn'),
    (8, '2023-10-03', 3803, 190150, 'Autumn'),
    (9, '2023-10-01', 4795, 239750, 'Autumn'),
    (9, '2023-10-02', 3201, 160050, 'Autumn'),
    (9, '2023-10-03', 3871, 193550, 'Autumn'),
    (10, '2023-10-01', 4568, 228400, 'Autumn'),
    (10, '2023-10-02', 5291, 264550, 'Autumn'),
    (10, '2023-10-03', 5212, 260600, 'Autumn');

-- =============================================
-- USER INTERACTIONS DATA
-- =============================================

-- Reviews for UNESCO World Heritage Sites
INSERT INTO USER_INTERACTIONS (user_id, site_id, interaction_type, interaction_date, rating, review)
VALUES
    -- Taj Mahal Reviews
    ('Arjun Sharma', 1, 'Review', '2024-01-15 10:00:00', 5, 'Amazing experience!'),
    ('Emily Wilson', 1, 'Review', '2024-01-16 14:30:00', 4, 'Beautiful architecture'),
    ('Rahul Kumar', 1, 'Review', '2024-07-01 09:15:00', 5, 'A masterpiece of architecture!'),
    ('Lisa Martinez', 1, 'Review', '2024-07-02 14:20:00', 4, 'Beautiful but crowded'),
    ('Sachin Verma', 1, 'Review', '2024-07-03 11:30:00', 5, 'Must visit at sunrise'),
    ('Oliver Thomas', 1, 'Review', '2024-07-04 16:45:00', 4, 'Historical significance'),
    ('Neha Mehta', 1, 'Review', '2024-07-05 10:00:00', 5, 'Symbol of eternal love'),

    -- Khajuraho Reviews
    ('Meera Iyer', 2, 'Review', '2024-01-20 11:15:00', 5, 'Must visit place'),
    ('Daniel Smith', 2, 'Review', '2024-07-06 13:15:00', 4, 'Intricate carvings'),
    ('Ankit Gupta', 2, 'Review', '2024-07-07 15:30:00', 5, 'Ancient art at its best'),
    ('Chloe Lee', 2, 'Review', '2024-07-08 09:45:00', 4, 'Well preserved'),
    ('Ravi Menon', 2, 'Review', '2024-07-09 11:20:00', 5, 'Cultural heritage'),
    ('Emma Johnson', 2, 'Review', '2024-07-10 14:35:00', 4, 'Architectural marvel'),

    -- Hampi Reviews
    ('Deepak Nair', 3, 'Review', '2024-01-10 09:45:00', 4, 'Rich in history'),
    ('Lucas Brown', 3, 'Review', '2024-07-11 10:50:00', 5, 'Ancient ruins'),
    ('Vinay Rathi', 3, 'Review', '2024-07-12 13:25:00', 4, 'Historical significance'),
    ('Nina Adams', 3, 'Review', '2024-07-13 15:40:00', 5, 'Must visit'),
    ('Anita Singh', 3, 'Review', '2024-07-14 09:55:00', 4, 'Rich history'),
    ('Jackson White', 3, 'Review', '2024-07-15 11:30:00', 5, 'UNESCO heritage');

-- Reviews for Non-UNESCO Heritage Sites
INSERT INTO USER_INTERACTIONS (user_id, site_id, interaction_type, interaction_date, rating, review)
VALUES
    -- Mysore Palace Reviews
    ('Krishna Murthy', 31, 'Review', '2024-07-01 10:00:00', 5, 'Magnificent palace!'),
    ('Sophia Turner', 31, 'Review', '2024-07-02 14:30:00', 4, 'Beautiful architecture'),

    -- Brihadeeswara Temple Reviews
    ('Ashok Pillai', 32, 'Review', '2024-07-03 11:15:00', 5, 'Ancient wonder'),

    -- Meenakshi Temple Reviews
    ('Rachel Green', 33, 'Review', '2024-07-04 09:45:00', 4, 'Spiritual experience'),

    -- Sundarbans Reviews
    ('Jyoti Banerjee', 34, 'Review', '2024-07-05 16:20:00', 5, 'Natural beauty'),

    -- Kaziranga Reviews
    ('Ethan Harris', 35, 'Review', '2024-07-06 13:10:00', 4, 'Wildlife paradise');

-- =============================================
-- SITE-ART FORM MAPPINGS
-- =============================================

-- UNESCO World Heritage Site Mappings
INSERT INTO SITE_ART_FORMS (site_id, art_form_id)
VALUES
    (1, 1), -- Taj Mahal - Kathakali
    (2, 2), -- Khajuraho - Madhubani
    (3, 3), -- Hampi - Pattachitra
    (4, 4), -- Konark - Chhau
    (5, 5), -- Ajanta - Warli
    (6, 6), -- Ellora - Kalamkari
    (7, 7), -- Mahabalipuram - Phulkari
    (8, 8), -- Sanchi - Gond
    (9, 9), -- Fatehpur Sikri - Kalamkari
    (10, 10), -- Qutub Minar - Kalamkari
    (11, 11), -- Red Fort - Kalamkari
    (12, 12), -- Chola Temples - Kalamkari
    (13, 13), -- Pattadakal - Kalamkari
    (14, 14), -- Elephanta Caves - Kalamkari
    (15, 15), -- Champaner-Pavagadh - Kalamkari
    (16, 16), -- Rani Ki Vav - Kalamkari
    (17, 17), -- Great Living Chola Temples - Kalamkari
    (18, 18), -- Group of Monuments at Hampi - Kalamkari
    (19, 19), -- Group of Monuments at Pattadakal - Kalamkari
    (20, 20); -- Buddhist Monuments at Sanchi - Kalamkari

-- Non-UNESCO Heritage Site Mappings
INSERT INTO SITE_ART_FORMS (site_id, art_form_id)
VALUES
    (31, 31), -- Mysore Palace - Yakshagana
    (32, 32), -- Brihadeeswara Temple - Theyyam
    (33, 33), -- Meenakshi Temple - Kalbelia
    (34, 34), -- Sundarbans - Bihu
    (35, 35); -- Kaziranga National Park - Dandiya Raas
