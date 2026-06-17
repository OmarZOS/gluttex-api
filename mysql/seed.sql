-- First, let's fix the foreign key issues by ensuring proper data flow

-- Insert app_user_type first (this is referenced by app_user)




-- Insert product_category (referenced by product)
INSERT INTO `gluttex`.`product_category` (`product_category_icon`) VALUES
('Baked Goods'),
('Spreads'),
('Cereals'),
('Pasta'),
('Snacks'),
('Beverages'),
('Desserts'),
('Frozen Foods'),
('Flours & Baking Ingredients'),
('Canned & Packaged Goods ');

-- Insert product_provider_type (referenced by product_provider)
INSERT INTO `gluttex`.`product_provider_type` (`product_provider_type_icon_url`) VALUES
('Restaurant'),
('Bakery'),
('Factory'),
('Supermarket'),
("Grocery Store"),
("Distributor");

-- Insert recipe_category (just for completeness)
INSERT INTO `gluttex`.`recipe_category` (`recipe_category_icon_url`) VALUES
("Appetizers & Snacks"),
("Soups & Stews"),
("Salads"),
("Main Courses"),
("Side Dishes"),
("Pasta & Noodles"),
("Casseroles"),
("Breakfast & Brunch"),
("Breads & Baking"),
("Desserts"),
("Drinks & Beverages"),
("Sauces & Condiments"),
("International Cuisine"),
("Healthy & Special Diets"),
("Holiday & Seasonal"),
("Kids & Family"),
("Slow Cooker & Instant Pot"),
("Quick & Easy"),
("One-Pan Recipes"),
("Grilling & BBQ");

-- Insert provider_details first (before product_provider)
INSERT INTO `gluttex`.`provider_details` (`provider_name`, `provider_contact_info`) VALUES
('Magasin habibou sans gluten', 'Facebook: https://www.facebook.com/profile.php?id=100063549909208'),
('Uno', 'Facebook: https://www.facebook.com/UNO.Hypermarche/, Instagram: https://www.instagram.com/uno_hypermarche/'),
('Superette université', 'N/A'),
('Corridors Shopping', 'N/A'),
('Caramel sans gluten', 'N/A');

select * from provider_details;


-- Insert product_provider with valid type IDs (1-6)
INSERT INTO `gluttex`.`product_provider` (`product_provider_details_id`, `product_provider_type_id`) VALUES
(1, 2),  -- Provider 1: Magasin habibou (Bakery)
(2, 4),  -- Provider 2: Uno (Supermarket)
(3, 4),  -- Provider 3: Superette université (Supermarket)
(4, 1),  -- Provider 4: Corridors Shopping (Restaurant)
(5, 4),  -- Provider 5: Caramel sans gluten (Supermarket)
(1, 2),  -- Provider 6: Another entry for Magasin habibou
(2, 4);  -- Provider 7: Another entry for Uno

-- Insert person_details first (before person)
INSERT INTO `gluttex`.`person_details` 
    (person_first_name, person_last_name, person_birth_date, person_gender, person_country_code) 
VALUES 
    ('Some', 'One', '2003-01-01', 'Male', '213');

-- Insert person with valid blood_type_id (1-8)
INSERT INTO `gluttex`.`person` 
    (person_details_id, person_blood_type) 
VALUES 
    (1, "B+"); 

-- Insert app_user with valid app_user_type_id (1-4) and person_id (1)
INSERT INTO `gluttex`.`app_user` 
    (app_user_name, app_user_password, app_user_person_id, app_user_type) 
VALUES 
    ('SomeOne', 'password', 1, "ADMIN"),
    ('ProviderAdmin', 'password', 1, "provider"),  -- Supplier user
    ('SellerUser', 'password', 1, "customer");     -- Seller user

-- Insert products with valid product_provider_id (1-7) and product_category_id (1-10)
-- Note: product_owner should reference valid app_user.id_app_user
INSERT INTO `gluttex`.`product` 
(`product_owner`,`product_name`, `product_brand`,`product_description`, `product_provider_id`, `product_category_id`, `product_barcode`, `product_price`, `product_quantity`,`last_updated`,`created`) VALUES
-- Products for provider 2
(2,'Grano''Sac Raisin Cacahuetes', 'Grano''Sac','Delicious gluten-free baked goods made with raisins and peanuts.', 2, 1, '1234567890123', 5.99, 100, CURDATE(), CURDATE()),
(2,'Butter Biscuits LEGER', 'LEGER','Light and crispy gluten-free butter biscuits.', 2, 1, '1234567890124', 4.49, 150, CURDATE(), CURDATE()),

-- Products for provider 3
(2,'Cookies', 'Home Bakery','Indulgent gluten-free cookies baked to perfection.', 3, 1, '1234567890125', 3.99, 200, CURDATE(), CURDATE()),
(2,'Gullon Cookies', 'Gullon','Classic gluten-free cookies from Gullon.', 3, 1, '1234567890126', 6.29, 120, CURDATE(), CURDATE()),

-- Products for provider 4
(2,'Date Butter', 'NutriLife','A rich and creamy date butter.', 4, 2, '1234567890127', 7.99, 80, CURDATE(), CURDATE()),

-- Products for provider 5
(2,'CARAIBE Crème à Tartiner', 'CARAIBE','Decadent chocolate spread from CARAIBE.', 5, 2, '1234567890128', 8.49, 100, CURDATE(), CURDATE()),

-- Products for provider 6
(2,'JUMPY Beurre De Cacahuète', 'JUMPY','Smooth and creamy peanut butter spread.', 6, 2, '1234567890129', 5.79, 90, CURDATE(), CURDATE()),

-- Products for provider 7
(2,'Semoule de pain', 'BioCereal','Organic gluten-free semolina.', 7, 3, '1234567890130', 3.99, 120, CURDATE(), CURDATE());

-- Insert provided_service_category first
INSERT INTO `gluttex`.`provided_service_category` (
  `provided_service_category_name`,
  `provided_service_category_icon_url`,
  `provided_service_category_avg_duration`,
  `provided_service_category_description`
) VALUES
('Blood Testing', 'https://example.com/icons/blood-test.svg', 30.00, 'Complete blood count, cholesterol, glucose, and other blood tests'),
('Diagnostic Imaging', 'https://example.com/icons/xray.svg', 45.00, 'X-rays, MRIs, CT scans, and ultrasound services'),
('Vaccination', 'https://example.com/icons/vaccine.svg', 15.00, 'Routine immunizations and travel vaccinations'),
('Health Check-up', 'https://example.com/icons/stethoscope.svg', 60.00, 'Comprehensive annual physical examinations'),
('Dental Care', 'https://example.com/icons/dental.svg', 40.00, 'Teeth cleaning, fillings, and basic dental procedures'),
('Pathology Tests', 'https://example.com/icons/microscope.svg', 120.00, 'Tissue biopsy analysis and histopathology'),
('Urine Analysis', 'https://example.com/icons/urine-test.svg', 20.00, 'Complete urinalysis and culture tests'),
('Allergy Testing', 'https://example.com/icons/allergy.svg', 90.00, 'Skin prick tests and allergen screening'),
('Genetic Testing', 'https://example.com/icons/dna.svg', 180.00, 'DNA analysis and genetic screening services'),
('Physiotherapy', 'https://example.com/icons/physical-therapy.svg', 50.00, 'Rehabilitation and physical therapy sessions'),
('Nutrition Counseling', 'https://example.com/icons/nutrition.svg', 45.00, 'Diet planning and nutritional guidance'),
('Mental Health Counseling', 'https://example.com/icons/mental-health.svg', 60.00, 'Therapy and psychological counseling sessions'),
('Acupuncture', 'https://example.com/icons/acupuncture.svg', 40.00, 'Traditional acupuncture therapy sessions'),
('Prenatal Care', 'https://example.com/icons/pregnancy.svg', 30.00, 'Pregnancy monitoring and prenatal check-ups'),
('Pediatric Care', 'https://example.com/icons/baby-care.svg', 25.00, 'Child healthcare and development monitoring'),
('Geriatric Care', 'https://example.com/icons/elderly-care.svg', 40.00, 'Elderly health monitoring and management'),
('Sports Medicine', 'https://example.com/icons/sports-medicine.svg', 50.00, 'Injury assessment and sports-related healthcare'),
('First Aid Training', 'https://example.com/icons/first-aid.svg', 240.00, 'CPR and emergency first aid certification'),
('Minor Surgery', 'https://example.com/icons/surgery.svg', 75.00, 'Outpatient minor surgical procedures'),
('Wound Care', 'https://example.com/icons/wound-care.svg', 25.00, 'Dressing changes and wound management'),
('IV Therapy', 'https://example.com/icons/iv-therapy.svg', 35.00, 'Intravenous hydration and vitamin therapy');

-- Insert provided_services with valid category_id (1-21) and product_provider_id (2-7)
-- Note: provided_service_product_provider_id should reference existing product_provider.id_product_provider
INSERT INTO `gluttex`.`provided_service` (
  `provided_service_name`,
  `provided_service_description`,
  `provided_service_category_id`,
  `provided_service_product_provider_id`,
  `provided_service_base_price`,
  `provided_service_final_price`,
  `provided_service_actual_duration`,
  `provided_service_is_active`,
  `provided_service_pricing_config`
) VALUES
-- Services for provider 2 (Blood Testing)
('Complete Blood Count (CBC)', 'Measures different components of blood', 1, 2, 25.0000, 20.0000, 25.00, 1, '{"discount_percent": 20}'),
('Lipid Profile Test', 'Measures cholesterol and triglyceride levels', 1, 2, 35.0000, 28.0000, 30.00, 1, '{"discount_percent": 20}'),
('Blood Glucose Test', 'Measures sugar levels for diabetes screening', 1, 2, 15.0000, 12.0000, 15.00, 1, '{"discount_percent": 20}'),

-- Services for provider 3 (Diagnostic Imaging)
('Chest X-Ray', 'Standard chest radiograph assessment', 2, 3, 80.0000, 65.0000, 20.00, 1, '{"insurance_coverage": 80}'),
('Abdominal Ultrasound', 'Imaging of abdominal organs', 2, 3, 120.0000, 95.0000, 45.00, 1, '{"insurance_coverage": 75}'),
('MRI Scan - Brain', 'Magnetic resonance imaging of the brain', 2, 3, 450.0000, 360.0000, 60.00, 1, '{"insurance_coverage": 70}'),

-- Services for provider 4 (Vaccination)
('Flu Vaccine', 'Annual influenza vaccination', 3, 4, 40.0000, 25.0000, 10.00, 1, '{"seasonal": true}'),
('COVID-19 Booster', 'Latest COVID-19 vaccine booster shot', 3, 4, 0.0000, 0.0000, 15.00, 1, '{"government_funded": true}'),
('Travel Vaccination Package', 'Vaccinations for international travel', 3, 4, 150.0000, 120.0000, 45.00, 1, '{"consultation_included": true}'),

-- Services for provider 5 (Health Check-up)
('Executive Health Screening', 'Comprehensive full-body check-up', 4, 5, 500.0000, 400.0000, 180.00, 1, '{"includes": ["blood_tests", "ecg"]}'),
('Basic Annual Check-up', 'Routine annual physical examination', 4, 5, 100.0000, 80.0000, 60.00, 1, '{"age_group": "adult"}'),
('Senior Citizen Health Package', 'Specialized check-up for elderly', 4, 5, 250.0000, 200.0000, 90.00, 1, '{"specialist_consultation": true}'),

-- Services for provider 6 (Dental Care)
('Teeth Cleaning & Polishing', 'Professional dental cleaning and scaling', 5, 6, 80.0000, 65.0000, 40.00, 1, '{"recommended_frequency": "6 months"}'),
('Dental Filling', 'Tooth cavity filling (per tooth)', 5, 6, 120.0000, 100.0000, 45.00, 1, '{"material_options": ["composite"]}'),
('Dental X-Ray', 'Intraoral dental imaging', 5, 6, 50.0000, 40.0000, 15.00, 1, '{"digital_imaging": true}'),

-- Services for provider 7 (Pathology Tests)
('Biopsy Analysis', 'Microscopic examination of tissue sample', 6, 7, 200.0000, 160.0000, 120.00, 1, '{"sample_type": "tissue"}'),
('Pap Smear Test', 'Cervical cancer screening test', 6, 7, 60.0000, 45.0000, 30.00, 1, '{"recommended_age": "21-65"}');

-- Insert service_staff_requirement with valid service_id (1-17)
INSERT INTO `gluttex`.`service_staff_requirement` (
  `service_staff_requirement_service_id`,
  `service_staff_requirement_min_count`,
  `service_staff_requirement_max_count`,
  `service_staff_requirement_hourly_rate`,
  `service_staff_requirement_allocated_hours`,
  `service_staff_requirement_notes`
) VALUES
-- Service 1 requirements
(1, 1, 2, 35.0000, 0.75, 'Certified phlebotomist'),
(1, 1, 1, 20.0000, 0.50, 'Prepare samples'),

-- Service 2 requirements
(2, 1, 1, 35.0000, 1.00, 'Fasting blood specialist'),
(2, 1, 1, 30.0000, 0.25, 'Patient preparation'),

-- Service 3 requirements
(3, 1, 1, 25.0000, 0.50, 'Glucose testing specialist'),
(3, 1, 1, 18.0000, 0.25, 'Patient check-in'),

-- Service 4 requirements
(4, 1, 2, 32.0000, 1.00, 'Liver function specialist'),
(4, 1, 1, 80.0000, 0.25, 'Results interpretation'),

-- Service 5 requirements
(5, 1, 1, 38.0000, 1.00, 'Thyroid testing specialist'),
(5, 1, 1, 100.0000, 0.50, 'Consultation and prescription'),

-- Service 6 requirements
(6, 1, 1, 40.0000, 0.75, 'Certified X-ray technician'),
(6, 1, 1, 120.0000, 0.25, 'Image interpretation'),

-- Service 7 requirements
(7, 1, 1, 45.0000, 1.25, 'Registered sonographer'),
(7, 1, 1, 120.0000, 0.50, 'Results interpretation'),

-- Service 8 requirements
(8, 1, 2, 55.0000, 2.00, 'Certified MRI specialist'),
(8, 1, 1, 150.0000, 1.00, 'Neuroradiology specialist'),

-- Service 9 requirements
(9, 1, 2, 50.0000, 1.00, 'CT scan specialist'),
(9, 1, 1, 45.0000, 0.25, 'Safety protocol'),

-- Service 10 requirements
(10, 1, 2, 32.0000, 0.50, 'Vaccination administration'),
(10, 1, 1, 45.0000, 0.25, 'Vaccine preparation'),

-- Service 11 requirements
(11, 1, 3, 35.0000, 0.50, 'COVID-19 specialist'),
(11, 1, 2, 22.0000, 0.50, 'Appointment scheduling'),

-- Service 12 requirements
(12, 1, 1, 60.0000, 1.50, 'International expert'),
(12, 1, 1, 55.0000, 0.75, 'Travel health assessment'),

-- Service 13 requirements
(13, 1, 1, 35.0000, 0.50, 'Adolescent vaccinations'),
(13, 1, 1, 95.0000, 0.25, 'HPV vaccine prescription'),

-- Service 14 requirements
(14, 1, 1, 150.0000, 3.00, 'Executive health specialist'),
(14, 1, 1, 180.0000, 0.50, 'Heart health consultation'),
(14,  2, 3, 32.0000, 4.00, 'Assist with tests'),

-- Service 15 requirements
(15, 1, 1, 120.0000, 1.50, 'Annual physical'),
(15, 1, 1, 25.0000, 1.00, 'Vital signs'),

-- Service 16 requirements
(16, 1, 1, 40.0000, 1.00, 'Teeth cleaning'),
(16, 1, 1, 80.0000, 0.50, 'Dental examination'),

-- Service 17 requirements
(17, 1, 1, 100.0000, 2.00, 'Biopsy analysis'),
(17, 1, 2, 35.0000, 1.50, 'Sample processing');

-- Insert service_resource_requirement with valid service_id (1-17) and product_ref (1-7)
INSERT INTO `gluttex`.`service_resource_requirement` (
  `service_resource_requirement_service_id`,
  `service_resource_requirement_name`,
  `service_resource_requirement_type`,
  `service_resource_requirement_quantity`,
  `service_resource_requirement_cost_per_unit`,
  `service_resource_requirement_is_consumable`,
  `service_resource_requirement_notes`,
  `service_resource_requirement_product_ref`
) VALUES
-- Service 1 resources
(1, 'Blood Collection Tube', 'Medical Supply', 3, 1.5000, 1, 'Vacutainer tubes', 1),
(1, 'Sterile Needle', 'Medical Supply', 1, 0.7500, 1, '21G safety needle', 1),
(1, 'Alcohol Swab', 'Medical Supply', 2, 0.2500, 1, 'Sterile preparation', NULL),

-- Service 2 resources
(2, 'Fasting Blood Test Kit', 'Test Kit', 1, 8.0000, 1, 'Lipid profile kit', 2),
(2, 'Centrifuge Tube', 'Lab Equipment', 1, 2.0000, 1, 'Sample separation', NULL),

-- Service 3 resources
(3, 'Glucose Test Strip', 'Medical Supply', 1, 3.5000, 1, 'Single-use strip', 1),
(3, 'Lancet Device', 'Medical Device', 1, 5.0000, 0, 'Finger prick device', 3),
(3, 'Control Solution', 'Chemical', 1, 4.0000, 1, 'Quality control', NULL),

-- Service 4 resources
(4, 'X-Ray Film', 'Imaging Supply', 1, 8.0000, 1, 'Digital imaging plate', 4),
(4, 'Lead Apron', 'Safety Equipment', 2, 45.0000, 0, 'Radiation protection', 3),
(4, 'Contrast Media', 'Chemical', 1, 35.0000, 1, 'Enhanced images', NULL),

-- Service 5 resources
(5, 'Ultrasound Gel', 'Medical Supply', 1, 5.0000, 1, 'Conduction gel', 1),
(5, 'Probe Cover', 'Medical Supply', 1, 1.2500, 1, 'Single-use protection', 1),
(5, 'Thermal Paper', 'Office Supply', 1, 2.0000, 1, 'Image printing', NULL),

-- Service 6 resources
(6, 'MRI Contrast Agent', 'Pharmaceutical', 1, 85.0000, 1, 'Gadolinium contrast', 2),
(6, 'Ear Protection', 'Safety Equipment', 1, 3.0000, 1, 'Noise reduction', NULL),

-- Service 7 resources
(7, 'Influenza Vaccine', 'Pharmaceutical', 1, 18.0000, 1, 'Quadrivalent flu vaccine', 2),
(7, 'Syringe with Needle', 'Medical Supply', 1, 0.8500, 1, '1ml safety syringe', 1),
(7, 'Sharps Container', 'Safety Equipment', 1, 3.5000, 0, 'Biohazard disposal', 3),

-- Service 8 resources
(8, 'COVID-19 Vaccine', 'Pharmaceutical', 1, 0.0000, 1, 'Government supplied', NULL),
(8, 'PPE Kit', 'Safety Equipment', 1, 4.5000, 1, 'Personal protection', 1),
(8, 'Vaccination Certificate', 'Document', 1, 1.0000, 1, 'Official proof', NULL),

-- Service 9 resources
(9, 'Travel Vaccine Package', 'Pharmaceutical', 3, 40.0000, 1, 'Multiple vaccines', 2),
(9, 'International Certificate', 'Document', 1, 5.0000, 1, 'Yellow fever certificate', NULL),

-- Service 10 resources
(10, 'ECG Electrodes', 'Medical Supply', 10, 1.2000, 1, 'Disposable ECG leads', 1),
(10, 'Spirometer Mouthpiece', 'Medical Supply', 1, 3.5000, 1, 'Lung function test', 1),
(10, 'Blood Pressure Cuff', 'Medical Device', 1, 25.0000, 0, 'Digital monitor', 3),

-- Service 11 resources
(11, 'Stethoscope', 'Medical Device', 1, 35.0000, 0, 'Clinical examination', 3),
(11, 'Otoscope Set', 'Medical Device', 1, 85.0000, 0, 'Ear examination', 3),
(11, 'Reflex Hammer', 'Medical Device', 1, 8.5000, 0, 'Neurological assessment', 3),

-- Service 12 resources
(12, 'Bone Density Phantom', 'Lab Equipment', 1, 150.0000, 0, 'DEXA calibration', NULL),
(12, 'Fall Risk Kit', 'Assessment Tool', 1, 45.0000, 0, 'Balance assessment', 3),
(12, 'Medication Software', 'Software', 1, 25.0000, 0, 'Annual subscription', NULL),

-- Service 13 resources
(13, 'Dental Prophy Paste', 'Dental Supply', 1, 4.5000, 1, 'Tooth polishing', 1),
(13, 'Disposable Prophy Angle', 'Dental Supply', 1, 2.7500, 1, 'Polishing attachment', 1),
(13, 'Dental Floss', 'Dental Supply', 1, 0.5000, 1, 'Patient education', NULL),

-- Service 14 resources
(14, 'Dental Composite', 'Dental Supply', 1, 15.0000, 1, 'Tooth-colored filling', 1),
(14, 'Curing Light', 'Dental Equipment', 1, 250.0000, 0, 'LED hardening light', 4),
(14, 'Dental Dam', 'Dental Supply', 1, 3.5000, 1, 'Isolation sheet', 1),

-- Service 15 resources
(15, 'Digital Sensor Cover', 'Dental Supply', 1, 1.2500, 1, 'Sterile barrier', 1),
(15, 'Bitewing Tabs', 'Dental Supply', 2, 0.7500, 1, 'X-ray positioning', NULL),
(15, 'Lead Thyroid Collar', 'Safety Equipment', 1, 12.0000, 0, 'Radiation protection', 3),

-- Service 16 resources
(16, 'Biopsy Cassette', 'Lab Supply', 1, 2.5000, 1, 'Tissue processing', NULL),
(16, 'Histology Slides', 'Lab Supply', 10, 0.8000, 1, 'Glass slides', 1),
(16, 'Staining Reagents', 'Chemical', 1, 25.0000, 1, 'H&E staining', 2),

-- Service 17 resources
(17, 'Pap Smear Kit', 'Test Kit', 1, 8.5000, 1, 'Collection set', 2),
(17, 'Cytology Fixative', 'Chemical', 1, 6.0000, 1, 'Preservative', NULL),
(17, 'Microscope Slides', 'Lab Supply', 5, 1.0000, 1, 'Examination slides', 1);

-- -- Insert carts with valid references
-- INSERT INTO `gluttex`.`cart` (
--   `cart_product_provider_id`,
--   `cart_selling_user`,
--   `cart_status`,
--   `cart_total_amount`,
--   `cart_notes`,
--   `cart_person_ref`
-- ) VALUES
-- -- Provider 2: Open carts (provider_id=2, selling_user=1, person_ref=1)
-- (2, 1, 'open', 85.5000, 'Lab tests pending selection', 1),
-- (2, 1, 'open', 120.0000, 'Follow-up tests needed', 1),

-- -- Provider 2: Pending/processing carts
-- (2, 1, 'pending', 220.7500, 'Waiting for insurance approval', 1),
-- (2, 1, 'pending', 95.2500, 'Payment processing', 1),

-- -- Provider 2: Completed carts
-- (2, 1, 'completed', 65.0000, 'Annual blood work completed on 2024-01-15', 1),
-- (2, 1, 'completed', 180.5000, 'Comprehensive health screening package', 1),
-- (2, 1, 'completed', 45.7500, 'Flu vaccination and basic checkup', 1),

-- -- Provider 3: Various status carts
-- (3, 1, 'open', 350.0000, 'MRI scan consultation', 1),
-- (3, 1, 'pending', 420.5000, 'CT scan scheduled for next week', 1),
-- (3, 1, 'completed', 280.0000, 'Ultrasound completed last month', 1),
-- (3, 1, 'completed', 150.0000, 'X-ray services - sports injury', 1),

-- -- Provider 4: Carts for different services
-- (4, 1, 'open', 600.0000, 'Executive health package under consideration', 1),
-- (4, 1, 'pending', 450.0000, 'Physiotherapy session package - awaiting confirmation', 1),
-- (4, 1, 'completed', 380.0000, 'Sports medicine consultation completed', 1),
-- (4, 1, 'canceled', 220.0000, 'Patient rescheduled acupuncture sessions', 1),

-- -- Provider 5: Vaccination and wellness carts
-- (5, 1, 'open', 0.0000, 'COVID-19 booster - free service', 1),
-- (5, 1, 'pending', 200.0000, 'HPV vaccination series - first dose administered', 1),
-- (5, 1, 'completed', 85.0000, 'Nutrition counseling - initial session', 1),
-- (5, 1, 'completed', 75.0000, 'Electro-acupuncture therapy completed', 1),

-- -- Provider 6: Travel and specialized services
-- (6, 1, 'open', 320.0000, 'Travel vaccination package for Europe trip', 1),
-- (6, 1, 'pending', 130.0000, 'Couples counseling - session package', 1),
-- (6, 1, 'completed', 79.0000, 'Ancestry DNA test results received', 1),
-- (6, 1, 'completed', 200.0000, 'Senior citizen health assessment completed', 1),

-- -- Provider 7: Various medical services
-- (7, 1, 'open', 95.0000, 'Dental cleaning appointment cart', 1),
-- (7, 1, 'pending', 165.0000, 'Dental filling procedure scheduled', 1),
-- (7, 1, 'completed', 40.0000, 'Dental X-ray completed', 1),
-- (7, 1, 'canceled', 100.0000, 'Patient opted for different provider', 1),

-- -- Additional carts with different statuses
-- (3, 1, 'open', 0.0000, 'Consultation cart - no services added yet', 1),
-- (4, 1, 'pending', 750.0000, 'Comprehensive diagnostic package - awaiting lab results', 1),
-- (5, 1, 'completed', 120.0000, 'Travel medicine consultation for Asia trip', 1),
-- (6, 1, 'open', 45.0000, 'Basic urinalysis test selection', 1),
-- (7, 1, 'pending', 300.0000, 'Dental crown procedure - mold taken', 1);

-- -- More varied cart examples
-- INSERT INTO `gluttex`.`cart` (
--   `cart_product_provider_id`,
--   `cart_selling_user`,
--   `cart_status`,
--   `cart_total_amount`,
--   `cart_notes`,
--   `cart_person_ref`
-- ) VALUES
-- (2, 1, 'completed', 560.0000, 'Full body checkup with specialist consultations', 1),
-- (3, 1, 'completed', 680.0000, 'MRI and CT scan package for neurological assessment', 1),
-- (4, 1, 'pending', 900.0000, 'Executive health screening with cardiology consult', 1),
-- (5, 1, 'canceled', 150.0000, 'Canceled due to schedule conflict', 1),
-- (6, 1, 'open', 250.0000, 'Genetic counseling and testing consideration', 1),
-- (7, 1, 'completed', 480.0000, 'Complete dental work including cleaning, filling, and X-ray', 1),
-- (2, 1, 'open', 35.0000, 'Single cholesterol test selection', 1),
-- (3, 1, 'pending', 1500.0000, 'Advanced imaging package - payment plan requested', 1),
-- (4, 1, 'completed', 320.0000, 'Physiotherapy sessions for back pain - completed course', 1),
-- (5, 1, 'open', 0.0000, 'Flu shot reminder cart', 1);

-- -- Insert ordered_services with valid cart_id (1-42) and service_id (1-17)
-- INSERT INTO `gluttex`.`ordered_service` (
--   `ordered_service_cart_id`,
--   `ordered_service_service_id`,
--   `ordered_service_quantity`,
--   `ordered_service_unit_price`,
--   `ordered_service_total_price`,
--   `ordered_service_notes`
-- ) VALUES
-- -- Cart 1-5: Blood Testing Services (services 1-3)
-- (1, 1, 1, 20.0000, 20.0000, 'Complete Blood Count test'),
-- (1, 2, 1, 28.0000, 28.0000, 'Lipid Profile with fasting'),
-- (1, 3, 1, 12.0000, 12.0000, 'Random blood glucose test'),

-- (2, 4, 1, 36.0000, 36.0000, 'Liver function test follow-up'),
-- (2, 5, 1, 48.0000, 48.0000, 'Thyroid panel re-check'),

-- (3, 1, 2, 20.0000, 40.0000, 'CBC for family - 2 persons'),
-- (3, 2, 2, 28.0000, 56.0000, 'Lipid tests for couple'),
-- (3, 3, 1, 12.0000, 12.0000, 'Single glucose test'),

-- (4, 4, 1, 36.0000, 36.0000, 'Annual liver function'),
-- (4, 5, 1, 48.0000, 48.0000, 'Thyroid monitoring'),

-- (5, 1, 1, 20.0000, 20.0000, 'Routine CBC'),
-- (5, 3, 1, 12.0000, 12.0000, 'Diabetes screening'),

-- -- Cart 6-10: Imaging Services (services 6-9)
-- (6, 6, 1, 65.0000, 65.0000, 'Chest X-ray for cough'),
-- (6, 7, 1, 95.0000, 95.0000, 'Abdominal ultrasound'),

-- (7, 8, 1, 360.0000, 360.0000, 'Brain MRI for headaches'),
-- (7, 9, 1, 240.0000, 240.0000, 'Follow-up CT scan'),

-- (8, 6, 1, 65.0000, 65.0000, 'Pre-employment chest X-ray'),
-- (8, 7, 1, 95.0000, 95.0000, 'Gallbladder ultrasound'),

-- (9, 8, 1, 360.0000, 360.0000, 'Neurological assessment MRI'),
-- (10, 9, 1, 240.0000, 240.0000, 'Chest CT for lung nodule'),

-- -- Cart 11-15: Vaccination Services (services 10-13)
-- (11, 10, 1, 25.0000, 25.0000, 'Annual flu shot'),
-- (11, 11, 1, 0.0000, 0.0000, 'COVID-19 booster'),

-- (12, 12, 1, 120.0000, 120.0000, 'Travel vaccination package'),
-- (12, 13, 1, 180.0000, 180.0000, 'HPV vaccine first dose'),

-- (13, 10, 2, 25.0000, 50.0000, 'Flu shots for couple'),
-- (13, 11, 2, 0.0000, 0.0000, 'COVID boosters for family'),

-- (14, 12, 1, 120.0000, 120.0000, 'Business travel vaccinations'),
-- (15, 13, 3, 180.0000, 540.0000, 'HPV vaccine for all 3 doses'),

-- -- Cart 16-20: Health Check-ups (services 14-15)
-- (16, 14, 1, 400.0000, 400.0000, 'Executive health screening'),
-- (16, 15, 1, 80.0000, 80.0000, 'Basic physical added'),

-- (17, 15, 1, 80.0000, 80.0000, 'Annual physical exam'),
-- (18, 14, 1, 400.0000, 400.0000, 'Corporate executive checkup'),

-- (19, 15, 2, 80.0000, 160.0000, 'Family physical exams'),

-- -- Cart 21-25: Dental Care (services 16-17)
-- (21, 16, 1, 65.0000, 65.0000, 'Teeth cleaning'),
-- (22, 17, 2, 100.0000, 200.0000, 'Two fillings needed'),
-- (22, 16, 1, 65.0000, 65.0000, 'Cleaning before fillings'),

-- (24, 16, 1, 65.0000, 65.0000, '6-month cleaning'),
-- (25, 17, 1, 100.0000, 100.0000, 'Single cavity filling'),

-- -- Cart 26-30: Pathology Tests (service 17)
-- (26, 17, 1, 160.0000, 160.0000, 'Skin biopsy analysis'),

-- -- Cart 31-35: Mixed Services
-- (31, 1, 1, 120.0000, 120.0000, 'Allergy skin testing'),
-- (32, 2, 1, 300.0000, 300.0000, 'Genetic carrier screening'),

-- (33, 3, 1, 75.0000, 75.0000, 'Initial physiotherapy assessment'),
-- (34, 4, 1, 85.0000, 85.0000, 'Nutrition consultation'),
-- (35, 5, 4, 100.0000, 400.0000, '4 therapy sessions package'),

-- -- Cart 36-42: Mixed Services
-- (36, 6, 2, 70.0000, 140.0000, '2 acupuncture sessions'),
-- (37, 7, 1, 100.0000, 100.0000, 'First trimester ultrasound'),

-- (38, 8, 1, 65.0000, 65.0000, 'Well-baby checkup'),
-- (39, 9, 1, 130.0000, 130.0000, 'Geriatric health assessment'),

-- (40, 10, 1, 100.0000, 100.0000, 'Sports injury evaluation'),
-- (41, 11, 1, 20.0000, 20.0000, 'Single test cart'),
-- (41, 10, 1, 25.0000, 25.0000, 'Flu shot only'),

-- (42, 16, 1, 65.0000, 65.0000, 'Dental cleaning'),
-- (42, 10, 1, 25.0000, 25.0000, 'Plus flu vaccination');

-- -- Insert ordered_items with valid product_id (1-7) and cart_ref (1-42)
-- INSERT INTO `gluttex`.`ordered_item` (
--   `ordered_product_id`,
--   `ordered_quantity`,
--   `applied_vat`,
--   `unit_price`,
--   `product_discount`,
--   `ordered_item_cart_ref`
-- ) VALUES
-- -- Cart 1: Blood test supplies (product IDs 1-4)
-- (1, 5, 8.0, 1.5000, 0.0, 1),    -- Blood Collection Tubes
-- (1, 10, 8.0, 0.7500, 10.0, 1),   -- Sterile Needles
-- (1, 20, 8.0, 0.2500, 0.0, 1),    -- Alcohol Swabs
-- (2, 1, 8.0, 8.0000, 15.0, 1),    -- Fasting Blood Test Kit

-- -- Cart 2: More lab supplies
-- (2, 2, 8.0, 12.0000, 5.0, 2),    -- Liver Function Reagents
-- (2, 1, 8.0, 25.0000, 10.0, 2),   -- Thyroid Assay Kit
-- (1, 3, 8.0, 0.5000, 0.0, 2),     -- Bandages

-- -- Cart 3: Imaging supplies
-- (4, 2, 18.0, 8.0000, 0.0, 3),    -- X-Ray Films
-- (3, 2, 18.0, 45.0000, 15.0, 3),  -- Lead Aprons
-- (2, 1, 18.0, 35.0000, 10.0, 3),  -- Contrast Media

-- -- Cart 4: Ultrasound supplies
-- (1, 3, 18.0, 5.0000, 5.0, 4),    -- Ultrasound Gel
-- (1, 5, 18.0, 1.2500, 0.0, 4),    -- Probe Covers

-- -- Cart 5: MRI supplies
-- (2, 1, 18.0, 85.0000, 20.0, 5),  -- MRI Contrast Agent
-- (3, 1, 18.0, 12.0000, 5.0, 5),   -- MRI Safe IV Set

-- -- Cart 6: Vaccination supplies
-- (2, 10, 5.0, 18.0000, 25.0, 6),  -- Flu Vaccines
-- (1, 12, 5.0, 0.8500, 10.0, 6),   -- Syringes with Needles
-- (3, 2, 5.0, 3.5000, 0.0, 6),     -- Sharps Containers

-- -- Cart 7: COVID vaccination supplies
-- (1, 25, 0.0, 4.5000, 0.0, 7),    -- PPE Kits

-- -- Cart 8: Travel vaccination package
-- (2, 5, 5.0, 40.0000, 15.0, 8),   -- Travel Vaccines

-- -- Cart 9: Dental supplies
-- (1, 10, 18.0, 4.5000, 10.0, 9),  -- Dental Prophy Paste
-- (1, 15, 18.0, 2.7500, 5.0, 9),   -- Disposable Prophy Angles
-- (1, 20, 18.0, 0.5000, 0.0, 9),   -- Dental Floss

-- -- Cart 10: Dental filling materials
-- (1, 5, 18.0, 15.0000, 15.0, 10), -- Dental Composite
-- (1, 10, 18.0, 3.5000, 5.0, 10),  -- Dental Dam
-- (4, 1, 18.0, 250.0000, 20.0, 10), -- Curing Light

-- -- Cart 11: X-ray dental supplies
-- (1, 20, 18.0, 1.2500, 5.0, 11),  -- Digital Sensor Covers
-- (3, 2, 18.0, 12.0000, 10.0, 11), -- Lead Thyroid Collars

-- -- Cart 12: Pathology lab supplies
-- (2, 5, 8.0, 25.0000, 15.0, 12),  -- Staining Reagents
-- (1, 50, 8.0, 0.8000, 20.0, 12),  -- Histology Slides

-- -- Cart 13: Urine test supplies
-- (1, 25, 8.0, 0.8500, 10.0, 13),  -- Urine Collection Cups
-- (2, 30, 8.0, 2.2500, 15.0, 13),  -- Urine Test Strips
-- (2, 10, 8.0, 4.5000, 20.0, 13),  -- Culture Media Plates

-- -- Cart 14: Allergy testing supplies
-- (2, 50, 8.0, 0.9500, 25.0, 14),  -- Allergen Extracts
-- (1, 60, 8.0, 0.1500, 30.0, 14),  -- Skin Test Lancets

-- -- Cart 15: Genetic testing supplies
-- (2, 3, 8.0, 350.0000, 20.0, 15), -- Carrier Screening Kits
-- (3, 1, 8.0, 25.0000, 10.0, 15),  -- Software Subscription

-- -- Cart 16: Physiotherapy equipment
-- (3, 2, 18.0, 25.0000, 15.0, 16), -- Blood Pressure Cuffs
-- (3, 1, 18.0, 35.0000, 10.0, 16), -- Stethoscopes
-- (3, 1, 18.0, 85.0000, 20.0, 16), -- Otoscope/Ophthalmoscope Set

-- -- Cart 17: Sports medicine equipment
-- (3, 1, 18.0, 45.0000, 15.0, 17), -- Fall Risk Assessment Kit
-- (3, 2, 18.0, 8.5000, 10.0, 17),  -- Reflex Hammers
-- (4, 1, 18.0, 150.0000, 25.0, 17), -- Bone Density Calibration

-- -- Cart 18: Single product orders
-- (1, 100, 8.0, 0.2500, 40.0, 18),  -- Bulk Alcohol Swabs
-- (2, 1, 18.0, 65.0000, 0.0, 19),   -- Single CT Contrast
-- (3, 3, 18.0, 12.0000, 10.0, 20),  -- Multiple IV Sets
-- (4, 2, 18.0, 8.0000, 5.0, 21),    -- X-Ray Films
-- (1, 50, 5.0, 0.8500, 30.0, 22),   -- Bulk Syringes

-- -- Cart 19-25: Mixed medical supplies
-- (2, 4, 8.0, 12.0000, 15.0, 23),   -- Liver Reagents
-- (1, 30, 8.0, 1.5000, 20.0, 24),   -- Blood Tubes
-- (3, 1, 18.0, 35.0000, 10.0, 25),  -- Stethoscope
-- (2, 2, 18.0, 85.0000, 25.0, 26),  -- MRI Contrast
-- (1, 15, 18.0, 4.5000, 15.0, 27),  -- Dental Paste
-- (2, 8, 5.0, 18.0000, 30.0, 28),   -- Flu Vaccines
-- (1, 40, 8.0, 0.8500, 35.0, 29),   -- Urine Cups

-- -- Cart 30-35: Business/wholesale orders
-- (1, 500, 8.0, 0.7500, 50.0, 30),  -- Wholesale Needles
-- (2, 100, 8.0, 2.2500, 40.0, 31),  -- Bulk Test Strips
-- (3, 25, 18.0, 3.5000, 35.0, 32),  -- Sharps Containers
-- (1, 200, 18.0, 5.0000, 30.0, 34), -- Ultrasound Gel
-- (2, 20, 18.0, 35.0000, 25.0, 35), -- Contrast Media

-- -- Cart 36-42: Final mixed carts
-- (1, 10, 8.0, 1.5000, 10.0, 36),   -- Blood Tubes
-- (2, 5, 8.0, 8.0000, 15.0, 37),    -- Test Kits
-- (3, 2, 18.0, 45.0000, 20.0, 38),  -- Lead Aprons
-- (1, 25, 5.0, 0.8500, 25.0, 40),   -- Syringes
-- (2, 1, 18.0, 250.0000, 30.0, 41), -- Curing Light
-- (3, 1, 8.0, 25.0000, 15.0, 42);   -- Software

-- -- Insert more varied orders
-- INSERT INTO `gluttex`.`ordered_item` (
--   `ordered_product_id`,
--   `ordered_quantity`,
--   `applied_vat`,
--   `unit_price`,
--   `product_discount`,
--   `ordered_item_cart_ref`
-- ) VALUES
-- -- Zero VAT items (medical essentials)
-- (1, 15, 0.0, 1.5000, 0.0, 1),
-- (2, 3, 0.0, 8.0000, 10.0, 2),

-- -- High VAT items (non-essential medical equipment)
-- (4, 1, 23.0, 250.0000, 15.0, 3),
-- (3, 2, 23.0, 85.0000, 20.0, 4),

-- -- Small orders for individual patients
-- (1, 5, 8.0, 0.2500, 0.0, 7),
-- (2, 1, 8.0, 25.0000, 5.0, 8),
-- (3, 1, 18.0, 35.0000, 10.0, 9),

-- -- Mixed VAT cart
-- (1, 10, 8.0, 1.5000, 10.0, 10),
-- (2, 2, 18.0, 35.0000, 15.0, 10),
-- (3, 1, 23.0, 85.0000, 20.0, 10),

-- -- Emergency order (no discount)
-- (1, 50, 8.0, 1.5000, 0.0, 11),
-- (2, 10, 8.0, 12.0000, 0.0, 11),

-- -- Seasonal sale items
-- (1, 20, 8.0, 4.5000, 50.0, 12),
-- (2, 5, 8.0, 18.0000, 40.0, 12),
-- (3, 3, 18.0, 12.0000, 30.0, 12);

-- -- Insert invoices with valid cart_id (1-42)
-- -- INSERT INTO `gluttex`.`invoice` (
-- --   `invoice_cart_id`,
-- --   `invoice_number`,
-- --   `invoice_total_amount`,
-- --   `invoice_status`,
-- --   `invoice_issue_date`,
-- --   `invoice_due_date`,
-- --   `invoice_notes`
-- -- ) VALUES
-- -- -- Cart 1-10: Various invoices
-- -- (1, 'INV-2024-001', 85.5000, 'paid', '2024-01-15', '2024-02-15', 'Complete blood work invoice'),
-- -- (2, 'INV-2024-002', 120.0000, 'paid', '2024-01-16', '2024-02-16', 'Follow-up tests invoice'),
-- -- (3, 'INV-2024-003', 220.7500, 'paid', '2024-01-17', '2024-02-17', 'Family tests package'),
-- -- (4, 'INV-2024-004', 95.2500, 'paid', '2024-01-18', '2024-02-18', 'Annual screening tests'),
-- -- (5, 'INV-2024-005', 65.0000, 'paid', '2024-01-19', '2024-02-19', 'Basic CBC screening'),
-- -- (6, 'INV-2024-006', 180.5000, 'paid', '2024-01-20', '2024-02-20', 'Chest X-ray and ultrasound'),
-- -- (7, 'INV-2024-007', 420.5000, 'paid', '2024-01-21', '2024-02-21', 'MRI and CT scan package'),
-- -- (8, 'INV-2024-008', 150.0000, 'paid', '2024-01-22', '2024-02-22', 'Pre-employment tests'),
-- -- (9, 'INV-2024-009', 280.0000, 'paid', '2024-01-23', '2024-02-23', 'Neurological MRI'),
-- -- (10, 'INV-2024-010', 240.0000, 'paid', '2024-01-24', '2024-02-24', 'CT scan follow-up'),

-- -- -- Cart 11-20: More invoices
-- -- (11, 'INV-2024-011', 25.0000, 'paid', '2024-01-25', '2024-02-25', 'Annual flu vaccination'),
-- -- (12, 'INV-2024-012', 300.0000, 'paid', '2024-01-26', '2024-02-26', 'Travel vaccination'),
-- -- (13, 'INV-2024-013', 50.0000, 'paid', '2024-01-27', '2024-02-27', 'Family flu shots'),
-- -- (14, 'INV-2024-014', 120.0000, 'paid', '2024-01-28', '2024-02-28', 'Business travel'),
-- -- (15, 'INV-2024-015', 540.0000, 'paid', '2024-01-29', '2024-02-29', 'HPV vaccine series'),
-- -- (16, 'INV-2024-016', 480.0000, 'paid', '2024-01-30', '2024-03-01', 'Executive health'),
-- -- (17, 'INV-2024-017', 280.0000, 'unpaid', '2024-02-01', '2024-03-01', 'Annual physical'),
-- -- (18, 'INV-2024-018', 400.0000, 'paid', '2024-02-02', '2024-03-02', 'Corporate checkup'),
-- -- (19, 'INV-2024-019', 160.0000, 'unpaid', '2024-02-03', '2024-03-03', 'Family exams'),
-- -- (20, 'INV-2024-020', 200.0000, 'paid', '2024-02-04', '2024-03-04', 'Geriatric assessment'),

-- -- -- Cart 21-30: More invoices
-- -- (21, 'INV-2024-021', 105.0000, 'paid', '2024-02-05', '2024-03-05', 'Dental cleaning'),
-- -- (22, 'INV-2024-022', 265.0000, 'paid', '2024-02-06', '2024-03-06', 'Dental fillings'),
-- -- (23, 'INV-2024-023', 40.0000, 'paid', '2024-02-07', '2024-03-07', 'Dental X-rays'),
-- -- (24, 'INV-2024-024', 65.0000, 'paid', '2024-02-08', '2024-03-08', '6-month cleaning'),
-- -- (25, 'INV-2024-025', 100.0000, 'unpaid', '2024-02-09', '2024-03-09', 'Single filling'),
-- -- (26, 'INV-2024-026', 205.0000, 'paid', '2024-02-10', '2024-03-10', 'Biopsy tests'),
-- -- (27, 'INV-2024-027', 160.0000, 'paid', '2024-02-11', '2024-03-11', 'Mole biopsy'),
-- -- (28, 'INV-2024-028', 45.0000, 'paid', '2024-02-12', '2024-03-12', 'Gynecological screening'),
-- -- (29, 'INV-2024-029', 56.0000, 'paid', '2024-02-13', '2024-03-13', 'UTI tests'),
-- -- (30, 'INV-2024-030', 20.0000, 'unpaid', '2024-02-14', '2024-03-14', 'Drug screening'),

-- -- -- Cart 31-42: More invoices
-- -- (31, 'INV-2024-031', 270.0000, 'paid', '2024-02-15', '2024-03-15', 'Allergy testing'),
-- -- (32, 'INV-2024-032', 379.0000, 'paid', '2024-02-16', '2024-03-16', 'Genetic testing'),
-- -- (33, 'INV-2024-033', 255.0000, 'unpaid', '2024-02-17', '2024-03-17', 'Physiotherapy'),
-- -- (34, 'INV-2024-034', 585.0000, 'paid', '2024-02-18', '2024-03-18', 'Weight management'),
-- -- (35, 'INV-2024-035', 530.0000, 'unpaid', '2024-02-19', '2024-03-19', 'Therapy package'),
-- -- (36, 'INV-2024-036', 215.0000, 'paid', '2024-02-20', '2024-03-20', 'Acupuncture'),
-- -- (37, 'INV-2024-037', 280.0000, 'paid', '2024-02-21', '2024-03-21', 'Prenatal care'),
-- -- (38, 'INV-2024-038', 165.0000, 'paid', '2024-02-22', '2024-03-22', 'Pediatric care'),
-- -- (39, 'INV-2024-039', 215.0000, 'unpaid', '2024-02-23', '2024-03-23', 'Geriatric care'),
-- -- (40, 'INV-2024-040', 230.0000, 'paid', '2024-02-24', '2024-03-24', 'Sports medicine'),
-- -- (41, 'INV-2024-041', 45.0000, 'paid', '2024-02-25', '2024-03-25', 'Single tests'),
-- -- (42, 'INV-2024-042', 130.0000, 'canceled', '2024-02-26', '2024-03-26', 'Dental + flu');

-- -- -- Insert more invoices
-- -- INSERT INTO `gluttex`.`invoice` (
-- --   `invoice_cart_id`,
-- --   `invoice_number`,
-- --   `invoice_total_amount`,
-- --   `invoice_status`,
-- --   `invoice_issue_date`,
-- --   `invoice_due_date`,
-- --   `invoice_notes`
-- -- ) VALUES
-- -- -- Past due invoices
-- -- (17, 'INV-2024-043', 280.0000, 'unpaid', '2024-01-15', '2024-02-15', 'PAST DUE - Annual physical'),
-- -- (19, 'INV-2024-044', 160.0000, 'unpaid', '2024-01-20', '2024-02-20', 'PAST DUE - Family exams'),
-- -- (25, 'INV-2024-045', 100.0000, 'unpaid', '2024-01-25', '2024-02-25', 'PAST DUE - Dental filling'),

-- -- -- Bulk/wholesale invoices
-- -- (5, 'INV-2024-048', 650.0000, 'paid', '2024-02-01', '2024-03-01', 'Corporate bulk order'),
-- -- (11, 'INV-2024-049', 250.0000, 'paid', '2024-02-05', '2024-03-05', 'Company flu program'),

-- -- -- Recent invoices
-- -- (17, 'INV-2024-054', 280.0000, 'unpaid', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 30 DAY), 'Current month invoice'),
-- -- (25, 'INV-2024-055', 100.0000, 'unpaid', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 30 DAY), 'Current dental work');

-- -- -- Insert payments with valid invoice_id (1-60)
-- -- INSERT INTO `gluttex`.`payment` (
-- --   `payment_invoice_id`,
-- --   `payment_amount`,
-- --   `payment_method`,
-- --   `payment_status`,
-- --   `payment_reference`,
-- --   `payment_notes`
-- -- ) VALUES
-- -- -- Full payments for invoices 1-10
-- -- (1, 85.5000, 'card', 'completed', 'TXN-00123456', 'Credit card payment'),
-- -- (2, 120.0000, 'bank', 'completed', 'BANK-78901234', 'Bank transfer'),
-- -- (3, 220.7500, 'card', 'completed', 'TXN-56789012', 'Debit card payment');


-- -- INSERT INTO `gluttex`.`cart` (
-- --   `cart_product_provider_id`,
-- --   `cart_selling_user`,
-- --   `cart_status`,
-- --   `cart_total_amount`,
-- --   `cart_notes`,
-- --   `cart_person_ref`
-- -- ) VALUES
-- -- -- Provider 2: Open carts
-- -- (2, 2, 'open', 85.5000, 'Lab tests pending selection', 2),
-- -- (2, 2, 'open', 120.0000, 'Follow-up tests needed', 2),

-- -- -- Provider 2: Pending/processing carts
-- -- (2, 2, 'pending', 220.7500, 'Waiting for insurance approval', 2),
-- -- (2, 2, 'pending', 95.2500, 'Payment processing', 2),

-- -- -- Provider 2: Completed carts
-- -- (2, 2, 'completed', 65.0000, 'Annual blood work completed on 2024-01-15', 2),
-- -- (2, 2, 'completed', 180.5000, 'Comprehensive health screening package', 2),
-- -- (2, 2, 'completed', 45.7500, 'Flu vaccination and basic checkup', 2),

-- -- -- Provider 3: Various status carts
-- -- (3, 2, 'open', 350.0000, 'MRI scan consultation', 2),
-- -- (3, 2, 'pending', 420.5000, 'CT scan scheduled for next week', 2),
-- -- (3, 2, 'completed', 280.0000, 'Ultrasound completed last month', 2),
-- -- (3, 2, 'completed', 150.0000, 'X-ray services - sports injury', 2),

-- -- -- Provider 4: Carts for different services
-- -- (4, 2, 'open', 600.0000, 'Executive health package under consideration', 2),
-- -- (4, 2, 'pending', 450.0000, 'Physiotherapy session package - awaiting confirmation', 2),
-- -- (4, 2, 'completed', 380.0000, 'Sports medicine consultation completed', 2),
-- -- (4, 2, 'canceled', 220.0000, 'Patient rescheduled acupuncture sessions', 2),

-- -- -- Provider 5: Vaccination and wellness carts
-- -- (5, 2, 'open', 0.0000, 'COVID-19 booster - free service', 2),
-- -- (5, 2, 'pending', 200.0000, 'HPV vaccination series - first dose administered', 2),
-- -- (5, 2, 'completed', 85.0000, 'Nutrition counseling - initial session', 2),
-- -- (5, 2, 'completed', 75.0000, 'Electro-acupuncture therapy completed', 2),

-- -- -- Provider 6: Travel and specialized services
-- -- (6, 2, 'open', 320.0000, 'Travel vaccination package for Europe trip', 2),
-- -- (6, 2, 'pending', 130.0000, 'Couples counseling - session package', 2),
-- -- (6, 2, 'completed', 79.0000, 'Ancestry DNA test results received', 2),
-- -- (6, 2, 'completed', 200.0000, 'Senior citizen health assessment completed', 2),

-- -- -- Provider 7: Various medical services
-- (7, 2, 'open', 95.0000, 'Dental cleaning appointment cart', 2),
-- (7, 2, 'pending', 165.0000, 'Dental filling procedure scheduled', 2),
-- (7, 2, 'completed', 40.0000, 'Dental X-ray completed', 2),
-- (7, 2, 'canceled', 100.0000, 'Patient opted for different provider', 2),

-- -- Additional carts with different statuses
-- (3, 2, 'open', 0.0000, 'Consultation cart - no services added yet', 2),
-- (4, 2, 'pending', 750.0000, 'Comprehensive diagnostic package - awaiting lab results', 2),
-- (5, 2, 'completed', 120.0000, 'Travel medicine consultation for Asia trip', 2),
-- (6, 2, 'open', 45.0000, 'Basic urinalysis test selection', 2),
-- (7, 2, 'pending', 300.0000, 'Dental crown procedure - mold taken', 2);

-- -- More varied cart examples
-- INSERT INTO `gluttex`.`cart` (
--   `cart_product_provider_id`,
--   `cart_selling_user`,
--   `cart_status`,
--   `cart_total_amount`,
--   `cart_notes`,
--   `cart_person_ref`
-- ) VALUES
-- (2, 2, 'completed', 560.0000, 'Full body checkup with specialist consultations', 2),
-- (3, 2, 'completed', 680.0000, 'MRI and CT scan package for neurological assessment', 2),
-- (4, 2, 'pending', 900.0000, 'Executive health screening with cardiology consult', 2),
-- (5, 2, 'canceled', 150.0000, 'Canceled due to schedule conflict', 2),
-- (6, 2, 'open', 250.0000, 'Genetic counseling and testing consideration', 2),
-- (7, 2, 'completed', 480.0000, 'Complete dental work including cleaning, filling, and X-ray', 2),
-- (2, 2, 'open', 35.0000, 'Single cholesterol test selection', 2),
-- (3, 2, 'pending', 1500.0000, 'Advanced imaging package - payment plan requested', 2),
-- (4, 2, 'completed', 320.0000, 'Physiotherapy sessions for back pain - completed course', 2),
-- (5, 2, 'open', 0.0000, 'Flu shot reminder cart', 2);

-- Insert dummy data for ordered_service table
-- INSERT INTO `gluttex`.`ordered_service` (
--   `ordered_service_cart_id`,
--   `ordered_service_service_id`,
--   `ordered_service_quantity`,
--   `ordered_service_unit_price`,
--   `ordered_service_total_price`,
--   `ordered_service_notes`
-- ) VALUES
-- -- Cart 1-5: Blood Testing Services
-- (1, 44, 1, 20.0000, 20.0000, 'Complete Blood Count test'),
-- (1, 45, 1, 28.0000, 28.0000, 'Lipid Profile with fasting'),
-- (1, 46, 1, 12.0000, 12.0000, 'Random blood glucose test'),

-- (2, 47, 1, 36.0000, 36.0000, 'Liver function test follow-up'),
-- (2, 48, 1, 48.0000, 48.0000, 'Thyroid panel re-check'),

-- (3, 44, 2, 20.0000, 40.0000, 'CBC for family - 2 persons'),
-- (3, 45, 2, 28.0000, 56.0000, 'Lipid tests for couple'),
-- (3, 46, 1, 12.0000, 12.0000, 'Single glucose test'),

-- (4, 47, 1, 36.0000, 36.0000, 'Annual liver function'),
-- (4, 48, 1, 48.0000, 48.0000, 'Thyroid monitoring'),

-- (5, 44, 1, 20.0000, 20.0000, 'Routine CBC'),
-- (5, 46, 1, 12.0000, 12.0000, 'Diabetes screening'),

-- -- Cart 6-10: Imaging Services
-- (6, 49, 1, 65.0000, 65.0000, 'Chest X-ray for cough'),
-- (6, 50, 1, 95.0000, 95.0000, 'Abdominal ultrasound'),

-- (7, 51, 1, 360.0000, 360.0000, 'Brain MRI for headaches'),
-- (7, 52, 1, 240.0000, 240.0000, 'Follow-up CT scan'),

-- (8, 49, 1, 65.0000, 65.0000, 'Pre-employment chest X-ray'),
-- (8, 50, 1, 95.0000, 95.0000, 'Gallbladder ultrasound'),

-- (9, 51, 1, 360.0000, 360.0000, 'Neurological assessment MRI'),

-- (10, 52, 1, 240.0000, 240.0000, 'Chest CT for lung nodule'),

-- -- Cart 11-15: Vaccination Services
-- (11, 53, 1, 25.0000, 25.0000, 'Annual flu shot'),
-- (11, 54, 1, 0.0000, 0.0000, 'COVID-19 booster'),

-- (12, 55, 1, 120.0000, 120.0000, 'Travel vaccination package'),
-- (12, 56, 1, 180.0000, 180.0000, 'HPV vaccine first dose'),

-- (13, 53, 2, 25.0000, 50.0000, 'Flu shots for couple'),
-- (13, 54, 2, 0.0000, 0.0000, 'COVID boosters for family'),

-- (14, 55, 1, 120.0000, 120.0000, 'Business travel vaccinations'),

-- (15, 56, 3, 180.0000, 540.0000, 'HPV vaccine for all 3 doses'),

-- -- Cart 16-20: Health Check-ups
-- (16, 57, 1, 400.0000, 400.0000, 'Executive health screening'),
-- (16, 58, 1, 80.0000, 80.0000, 'Basic physical added'),

-- (17, 58, 1, 80.0000, 80.0000, 'Annual physical exam'),
-- (17, 59, 1, 200.0000, 200.0000, 'Elderly parent check-up'),

-- (18, 57, 1, 400.0000, 400.0000, 'Corporate executive checkup'),

-- (19, 58, 2, 80.0000, 160.0000, 'Family physical exams'),

-- (20, 59, 1, 200.0000, 200.0000, 'Geriatric assessment'),

-- -- Cart 21-25: Dental Care
-- (21, 60, 1, 65.0000, 65.0000, 'Teeth cleaning'),
-- (21, 62, 1, 40.0000, 40.0000, 'Dental X-rays'),

-- (22, 61, 2, 100.0000, 200.0000, 'Two fillings needed'),
-- (22, 60, 1, 65.0000, 65.0000, 'Cleaning before fillings'),

-- (23, 62, 1, 40.0000, 40.0000, 'Routine dental X-rays'),

-- (24, 60, 1, 65.0000, 65.0000, '6-month cleaning'),

-- (25, 61, 1, 100.0000, 100.0000, 'Single cavity filling'),

-- -- Cart 26-30: Pathology & Lab Tests
-- (26, 63, 1, 160.0000, 160.0000, 'Skin biopsy analysis'),
-- (26, 64, 1, 45.0000, 45.0000, 'Routine pap smear'),

-- (27, 63, 1, 160.0000, 160.0000, 'Mole biopsy'),

-- (28, 64, 1, 45.0000, 45.0000, 'Annual gynecological screening'),

-- (29, 65, 1, 20.0000, 20.0000, 'Urinalysis for UTI'),
-- (29, 66, 1, 36.0000, 36.0000, 'Urine culture'),

-- (30, 65, 1, 20.0000, 20.0000, 'Pre-employment drug screen'),

-- -- Cart 31-35: Specialized Services
-- (31, 67, 1, 120.0000, 120.0000, 'Allergy skin testing'),
-- (31, 68, 1, 150.0000, 150.0000, 'Food allergy panel'),

-- (32, 69, 1, 300.0000, 300.0000, 'Genetic carrier screening'),
-- (32, 70, 1, 79.0000, 79.0000, 'Ancestry DNA test'),

-- (33, 71, 1, 75.0000, 75.0000, 'Initial physiotherapy assessment'),
-- (33, 72, 3, 60.0000, 180.0000, '3 massage therapy sessions'),

-- (34, 73, 1, 85.0000, 85.0000, 'Nutrition consultation'),
-- (34, 74, 1, 500.0000, 500.0000, 'Weight management program'),

-- (35, 75, 4, 100.0000, 400.0000, '4 therapy sessions package'),
-- (35, 76, 1, 130.0000, 130.0000, 'Couples counseling'),

-- -- Cart 36-42: Mixed Services
-- (36, 77, 2, 70.0000, 140.0000, '2 acupuncture sessions'),
-- (36, 78, 1, 75.0000, 75.0000, 'Electro-acupuncture'),

-- (37, 79, 1, 100.0000, 100.0000, 'First trimester ultrasound'),
-- (37, 80, 1, 180.0000, 180.0000, 'Prenatal blood work'),

-- (38, 81, 1, 65.0000, 65.0000, 'Well-baby checkup'),
-- (38, 82, 1, 100.0000, 100.0000, 'Child development assessment'),

-- (39, 83, 1, 130.0000, 130.0000, 'Geriatric health assessment'),
-- (39, 84, 1, 85.0000, 85.0000, 'Fall risk evaluation'),

-- (40, 85, 1, 100.0000, 100.0000, 'Sports injury evaluation'),
-- (40, 86, 1, 130.0000, 130.0000, 'Athletic performance consultation'),

-- (41, 44, 1, 20.0000, 20.0000, 'Single test cart'),
-- (41, 53, 1, 25.0000, 25.0000, 'Flu shot only'),

-- (42, 60, 1, 65.0000, 65.0000, 'Dental cleaning'),
-- (42, 62, 1, 40.0000, 40.0000, 'With X-rays'),
-- (42, 53, 1, 25.0000, 25.0000, 'Plus flu vaccination');




-- Insert dummy data for ordered_item table
-- INSERT INTO `gluttex`.`ordered_item` (
--   `ordered_product_id`,
--   `ordered_quantity`,
--   `applied_vat`,
--   `unit_price`,
--   `product_discount`,
--   `ordered_item_cart_ref`
-- ) VALUES
-- -- Cart 1: Blood test supplies (product IDs 8-11)
-- (8, 5, 8.0, 1.5000, 0.0, 1),    -- Blood Collection Tubes
-- (8, 10, 8.0, 0.7500, 10.0, 1),   -- Sterile Needles
-- (8, 20, 8.0, 0.2500, 0.0, 1),    -- Alcohol Swabs
-- (9, 1, 8.0, 8.0000, 15.0, 1),    -- Fasting Blood Test Kit

-- -- Cart 2: More lab supplies
-- (9, 2, 8.0, 12.0000, 5.0, 2),    -- Liver Function Reagents
-- (9, 1, 8.0, 25.0000, 10.0, 2),   -- Thyroid Assay Kit
-- (8, 3, 8.0, 0.5000, 0.0, 2),     -- Bandages

-- -- Cart 3: Imaging supplies
-- (11, 2, 18.0, 8.0000, 0.0, 3),   -- X-Ray Films
-- (10, 2, 18.0, 45.0000, 15.0, 3), -- Lead Aprons
-- (9, 1, 18.0, 35.0000, 10.0, 3),  -- Contrast Media

-- -- Cart 4: Ultrasound supplies
-- (8, 3, 18.0, 5.0000, 5.0, 4),    -- Ultrasound Gel
-- (8, 5, 18.0, 1.2500, 0.0, 4),    -- Probe Covers
-- (11, 1, 18.0, 2.0000, 0.0, 4),   -- Thermal Paper

-- -- Cart 5: MRI supplies
-- (9, 1, 18.0, 85.0000, 20.0, 5),  -- MRI Contrast Agent
-- (10, 1, 18.0, 12.0000, 5.0, 5),  -- MRI Safe IV Set
-- (NULL, 2, 18.0, 3.0000, 0.0, 5), -- Ear Protection (no product ref)

-- -- Cart 6: Vaccination supplies
-- (9, 10, 5.0, 18.0000, 25.0, 6),  -- Flu Vaccines
-- (8, 12, 5.0, 0.8500, 10.0, 6),   -- Syringes with Needles
-- (10, 2, 5.0, 3.5000, 0.0, 6),    -- Sharps Containers

-- -- Cart 7: COVID vaccination supplies
-- (8, 25, 0.0, 4.5000, 0.0, 7),    -- PPE Kits (no VAT for medical emergency)
-- (NULL, 50, 0.0, 1.0000, 0.0, 7), -- Vaccination Certificates

-- -- Cart 8: Travel vaccination package
-- (9, 5, 5.0, 40.0000, 15.0, 8),   -- Travel Vaccines
-- (NULL, 2, 5.0, 5.0000, 0.0, 8),  -- International Certificates
-- (NULL, 5, 5.0, 2.5000, 20.0, 8), -- Travel Health Guides

-- -- Cart 9: Dental supplies
-- (8, 10, 18.0, 4.5000, 10.0, 9),  -- Dental Prophy Paste
-- (8, 15, 18.0, 2.7500, 5.0, 9),   -- Disposable Prophy Angles
-- (8, 20, 18.0, 0.5000, 0.0, 9),   -- Dental Floss

-- -- Cart 10: Dental filling materials
-- (8, 5, 18.0, 15.0000, 15.0, 10), -- Dental Composite
-- (8, 10, 18.0, 3.5000, 5.0, 10),  -- Dental Dam
-- (11, 1, 18.0, 250.0000, 20.0, 10), -- Curing Light (equipment)

-- -- Cart 11: X-ray dental supplies
-- (8, 20, 18.0, 1.2500, 5.0, 11),  -- Digital Sensor Covers
-- (10, 2, 18.0, 12.0000, 10.0, 11), -- Lead Thyroid Collars
-- (NULL, 10, 18.0, 0.7500, 0.0, 11), -- Bitewing Tabs

-- -- Cart 12: Pathology lab supplies
-- (9, 5, 8.0, 25.0000, 15.0, 12),  -- Staining Reagents
-- (8, 50, 8.0, 0.8000, 20.0, 12),  -- Histology Slides
-- (NULL, 20, 8.0, 2.5000, 5.0, 12), -- Biopsy Cassettes

-- -- Cart 13: Urine test supplies
-- (8, 25, 8.0, 0.8500, 10.0, 13),  -- Urine Collection Cups
-- (9, 30, 8.0, 2.2500, 15.0, 13),  -- Urine Test Strips
-- (9, 10, 8.0, 4.5000, 20.0, 13),  -- Culture Media Plates

-- -- Cart 14: Allergy testing supplies
-- (9, 50, 8.0, 0.9500, 25.0, 14),  -- Allergen Extracts
-- (8, 60, 8.0, 0.1500, 30.0, 14),  -- Skin Test Lancets
-- (NULL, 5, 8.0, 3.5000, 0.0, 14), -- Measuring Rulers

-- -- Cart 15: Genetic testing supplies
-- (9, 3, 8.0, 350.0000, 20.0, 15), -- Carrier Screening Kits
-- (NULL, 2, 8.0, 99.0000, 25.0, 15), -- Ancestry DNA Kits
-- (10, 1, 8.0, 25.0000, 10.0, 15), -- Software Subscription

-- -- Cart 16: Physiotherapy equipment
-- (10, 2, 18.0, 25.0000, 15.0, 16), -- Blood Pressure Cuffs
-- (10, 1, 18.0, 35.0000, 10.0, 16), -- Stethoscopes
-- (10, 1, 18.0, 85.0000, 20.0, 16), -- Otoscope/Ophthalmoscope Set

-- -- Cart 17: Sports medicine equipment
-- (10, 1, 18.0, 45.0000, 15.0, 17), -- Fall Risk Assessment Kit
-- (10, 2, 18.0, 8.5000, 10.0, 17),  -- Reflex Hammers
-- (11, 1, 18.0, 150.0000, 25.0, 17), -- Bone Density Calibration

-- -- Cart 18: Single product orders
-- (8, 100, 8.0, 0.2500, 40.0, 18),  -- Bulk Alcohol Swabs
-- (9, 1, 18.0, 65.0000, 0.0, 19),   -- Single CT Contrast
-- (10, 3, 18.0, 12.0000, 10.0, 20), -- Multiple IV Sets
-- (11, 2, 18.0, 8.0000, 5.0, 21),   -- X-Ray Films
-- (8, 50, 5.0, 0.8500, 30.0, 22),   -- Bulk Syringes

-- -- Cart 19-25: Mixed medical supplies
-- (9, 4, 8.0, 12.0000, 15.0, 23),   -- Liver Reagents
-- (8, 30, 8.0, 1.5000, 20.0, 24),   -- Blood Tubes
-- (10, 1, 18.0, 35.0000, 10.0, 25), -- Stethoscope
-- (9, 2, 18.0, 85.0000, 25.0, 26),  -- MRI Contrast
-- (8, 15, 18.0, 4.5000, 15.0, 27),  -- Dental Paste
-- (9, 8, 5.0, 18.0000, 30.0, 28),   -- Flu Vaccines
-- (8, 40, 8.0, 0.8500, 35.0, 29),   -- Urine Cups

-- -- Cart 30-35: Business/wholesale orders
-- (8, 500, 8.0, 0.7500, 50.0, 30),  -- Wholesale Needles
-- (9, 100, 8.0, 2.2500, 40.0, 31),  -- Bulk Test Strips
-- (10, 25, 18.0, 3.5000, 35.0, 32), -- Sharps Containers
-- (11, 50, 18.0, 1.2500, 45.0, 33), -- Sensor Covers
-- (8, 200, 18.0, 5.0000, 30.0, 34), -- Ultrasound Gel
-- (9, 20, 18.0, 35.0000, 25.0, 35), -- Contrast Media

-- -- Cart 36-42: Final mixed carts
-- (8, 10, 8.0, 1.5000, 10.0, 36),   -- Blood Tubes
-- (9, 5, 8.0, 8.0000, 15.0, 37),    -- Test Kits
-- (10, 2, 18.0, 45.0000, 20.0, 38), -- Lead Aprons
-- (11, 3, 18.0, 2.0000, 0.0, 39),   -- Thermal Paper
-- (8, 25, 5.0, 0.8500, 25.0, 40),   -- Syringes
-- (9, 1, 18.0, 250.0000, 30.0, 41), -- Curing Light
-- (10, 1, 8.0, 25.0000, 15.0, 42);  -- Software



-- More varied orders with different scenarios
-- INSERT INTO `gluttex`.`ordered_item` (
--   `ordered_product_id`,
--   `ordered_quantity`,
--   `applied_vat`,
--   `unit_price`,
--   `product_discount`,
--   `ordered_item_cart_ref`
-- ) VALUES
-- -- Zero VAT items (medical essentials)
-- (8, 15, 0.0, 1.5000, 0.0, 1),
-- (9, 3, 0.0, 8.0000, 10.0, 2),

-- -- High VAT items (non-essential medical equipment)
-- (11, 1, 23.0, 250.0000, 15.0, 3),
-- (10, 2, 23.0, 85.0000, 20.0, 4),

-- -- Bulk orders with tiered discounts
-- (8, 1000, 8.0, 0.7500, 60.0, 5),
-- (9, 500, 8.0, 2.2500, 55.0, 6),

-- -- Small orders for individual patients
-- (8, 5, 8.0, 0.2500, 0.0, 7),
-- (9, 1, 8.0, 25.0000, 5.0, 8),
-- (10, 1, 18.0, 35.0000, 10.0, 9),

-- -- Mixed VAT cart
-- (8, 10, 8.0, 1.5000, 10.0, 10),
-- (9, 2, 18.0, 35.0000, 15.0, 10),
-- (10, 1, 23.0, 85.0000, 20.0, 10),

-- -- Emergency order (no discount)
-- (8, 50, 8.0, 1.5000, 0.0, 11),
-- (9, 10, 8.0, 12.0000, 0.0, 11),

-- -- Seasonal sale items
-- (8, 20, 8.0, 4.5000, 50.0, 12),
-- (9, 5, 8.0, 18.0000, 40.0, 12),
-- (10, 3, 18.0, 12.0000, 30.0, 12);


-- -- Insert dummy data for ordered_item table referencing placed_order (IDs 38-74)
-- INSERT INTO `gluttex`.`ordered_item` (
--   `ordered_product_id`,
--   `ordered_quantity`,
--   `applied_vat`,
--   `order_ref`,
--   `unit_price`,
--   `product_discount`,
--   `ordered_item_cart_ref`
-- ) VALUES
-- -- Order 38: Blood test supplies order
-- (8, 10, 8.0, 38, 1.5000, 10.0, NULL),    -- Blood Collection Tubes
-- (8, 20, 8.0, 38, 0.7500, 15.0, NULL),    -- Sterile Needles
-- (8, 30, 8.0, 38, 0.2500, 0.0, NULL),     -- Alcohol Swabs
-- (9, 5, 8.0, 38, 8.0000, 20.0, NULL),     -- Fasting Blood Test Kits

-- -- Order 39: Imaging supplies order
-- (11, 5, 18.0, 39, 8.0000, 5.0, NULL),    -- X-Ray Films
-- (10, 2, 18.0, 39, 45.0000, 15.0, NULL),  -- Lead Aprons
-- (9, 3, 18.0, 39, 35.0000, 10.0, NULL),   -- Contrast Media

-- -- Order 40: Vaccination supplies
-- (9, 25, 5.0, 40, 18.0000, 25.0, NULL),   -- Flu Vaccines
-- (8, 30, 5.0, 40, 0.8500, 20.0, NULL),    -- Syringes with Needles
-- (10, 5, 5.0, 40, 3.5000, 10.0, NULL),    -- Sharps Containers

-- -- Order 41: Dental supplies package
-- (8, 25, 18.0, 41, 4.5000, 15.0, NULL),   -- Dental Prophy Paste
-- (8, 30, 18.0, 41, 2.7500, 10.0, NULL),   -- Disposable Prophy Angles
-- (8, 50, 18.0, 41, 0.5000, 5.0, NULL),    -- Dental Floss

-- -- Order 42: Dental equipment order
-- (8, 10, 18.0, 42, 15.0000, 20.0, NULL),  -- Dental Composite
-- (11, 1, 18.0, 42, 250.0000, 25.0, NULL), -- Curing Light
-- (10, 2, 18.0, 42, 12.0000, 15.0, NULL),  -- Lead Thyroid Collars

-- -- Order 43: Lab pathology supplies
-- (9, 10, 8.0, 43, 25.0000, 20.0, NULL),   -- Staining Reagents
-- (8, 100, 8.0, 43, 0.8000, 30.0, NULL),   -- Histology Slides
-- (NULL, 30, 8.0, 43, 2.5000, 10.0, NULL), -- Biopsy Cassettes

-- -- Order 44: Urine test supplies bulk
-- (8, 50, 8.0, 44, 0.8500, 25.0, NULL),    -- Urine Collection Cups
-- (9, 50, 8.0, 44, 2.2500, 20.0, NULL),    -- Urine Test Strips
-- (9, 20, 8.0, 44, 4.5000, 15.0, NULL),    -- Culture Media Plates

-- -- Order 45: Allergy testing supplies
-- (9, 100, 8.0, 45, 0.9500, 30.0, NULL),   -- Allergen Extracts
-- (8, 120, 8.0, 45, 0.1500, 35.0, NULL),   -- Skin Test Lancets
-- (NULL, 10, 8.0, 45, 3.5000, 0.0, NULL),  -- Measuring Rulers

-- -- Order 46: Genetic testing order
-- (9, 5, 8.0, 46, 350.0000, 25.0, NULL),   -- Carrier Screening Kits
-- (NULL, 3, 8.0, 46, 99.0000, 30.0, NULL), -- Ancestry DNA Kits
-- (10, 1, 8.0, 46, 25.0000, 15.0, NULL),   -- Software Subscription

-- -- Order 47: Physiotherapy equipment
-- (10, 3, 18.0, 47, 25.0000, 20.0, NULL),  -- Blood Pressure Cuffs
-- (10, 2, 18.0, 47, 35.0000, 15.0, NULL),  -- Stethoscopes
-- (10, 1, 18.0, 47, 85.0000, 25.0, NULL),  -- Otoscope/Ophthalmoscope Set

-- -- Order 48: Sports medicine equipment
-- (10, 2, 18.0, 48, 45.0000, 20.0, NULL),  -- Fall Risk Assessment Kits
-- (10, 5, 18.0, 48, 8.5000, 15.0, NULL),   -- Reflex Hammers
-- (11, 1, 18.0, 48, 150.0000, 30.0, NULL), -- Bone Density Calibration

-- -- Order 49: COVID supplies (zero VAT)
-- (8, 100, 0.0, 49, 4.5000, 0.0, NULL),    -- PPE Kits
-- (NULL, 200, 0.0, 49, 1.0000, 0.0, NULL), -- Vaccination Certificates
-- (8, 50, 0.0, 49, 0.8500, 0.0, NULL),     -- Syringes

-- -- Order 50: Travel medicine package
-- (9, 10, 5.0, 50, 40.0000, 20.0, NULL),   -- Travel Vaccines
-- (NULL, 5, 5.0, 50, 5.0000, 10.0, NULL),  -- International Certificates
-- (NULL, 10, 5.0, 50, 2.5000, 15.0, NULL), -- Travel Health Guides

-- -- Order 51: Single product bulk order
-- (8, 500, 8.0, 51, 0.7500, 50.0, NULL),   -- Sterile Needles (bulk)

-- -- Order 52: Mixed medical supplies
-- (9, 8, 8.0, 52, 12.0000, 20.0, NULL),    -- Liver Function Reagents
-- (8, 50, 8.0, 52, 1.5000, 25.0, NULL),    -- Blood Collection Tubes
-- (9, 3, 18.0, 52, 85.0000, 30.0, NULL),   -- MRI Contrast Agent

-- -- Order 53: Dental X-ray supplies
-- (8, 40, 18.0, 53, 1.2500, 20.0, NULL),   -- Digital Sensor Covers
-- (10, 3, 18.0, 53, 12.0000, 15.0, NULL),  -- Lead Thyroid Collars
-- (NULL, 20, 18.0, 53, 0.7500, 10.0, NULL),-- Bitewing Tabs

-- -- Order 54: Emergency order (no discounts)
-- (8, 25, 8.0, 54, 1.5000, 0.0, NULL),     -- Blood Tubes
-- (9, 5, 8.0, 54, 12.0000, 0.0, NULL),     -- Liver Reagents
-- (8, 10, 8.0, 54, 0.2500, 0.0, NULL),     -- Alcohol Swabs

-- -- Order 55: Seasonal flu prevention
-- (9, 50, 5.0, 55, 18.0000, 35.0, NULL),   -- Flu Vaccines
-- (8, 60, 5.0, 55, 0.8500, 30.0, NULL),    -- Syringes
-- (10, 8, 5.0, 55, 3.5000, 20.0, NULL),    -- Sharps Containers

-- -- Order 56: Hospital equipment order
-- (11, 3, 23.0, 56, 250.0000, 40.0, NULL), -- Curing Lights
-- (10, 5, 23.0, 56, 85.0000, 35.0, NULL),  -- Otoscope Sets
-- (11, 2, 23.0, 56, 150.0000, 30.0, NULL), -- Bone Density Equipment

-- -- Order 57: Small clinic order
-- (8, 15, 8.0, 57, 4.5000, 10.0, NULL),    -- Dental Paste
-- (9, 5, 8.0, 57, 8.0000, 15.0, NULL),     -- Test Kits
-- (8, 20, 8.0, 57, 0.5000, 5.0, NULL),     -- Dental Floss

-- -- Order 58: Wholesale needles
-- (8, 1000, 8.0, 58, 0.7500, 60.0, NULL),  -- Sterile Needles (wholesale)

-- -- Order 59: Test strips bulk
-- (9, 200, 8.0, 59, 2.2500, 55.0, NULL),   -- Urine Test Strips

-- -- Order 60: Mixed VAT order
-- (8, 20, 8.0, 60, 1.5000, 15.0, NULL),    -- Blood Tubes (8% VAT)
-- (9, 5, 18.0, 60, 35.0000, 20.0, NULL),   -- Contrast Media (18% VAT)
-- (11, 1, 23.0, 60, 250.0000, 25.0, NULL), -- Equipment (23% VAT)

-- -- Order 61: Single item order
-- (10, 1, 18.0, 61, 35.0000, 10.0, NULL),  -- Single Stethoscope

-- -- Order 62: Two items order
-- (8, 10, 8.0, 62, 0.8500, 15.0, NULL),    -- Syringes
-- (9, 2, 8.0, 62, 25.0000, 20.0, NULL),    -- Staining Reagents

-- -- Order 63: Free medical supplies (zero cost)
-- (8, 50, 0.0, 63, 0.0000, 100.0, NULL),   -- Donated supplies
-- (9, 10, 0.0, 63, 0.0000, 100.0, NULL),   -- Donated test kits

-- -- Order 64: High-value equipment
-- (11, 2, 23.0, 64, 1200.0000, 35.0, NULL),-- Advanced Imaging Equipment
-- (10, 3, 23.0, 64, 450.0000, 30.0, NULL), -- Specialized Medical Devices

-- -- Order 65: Regular restocking order
-- (8, 100, 8.0, 65, 1.5000, 25.0, NULL),   -- Blood Tubes
-- (8, 200, 8.0, 65, 0.7500, 30.0, NULL),   -- Needles
-- (8, 300, 8.0, 65, 0.2500, 20.0, NULL),   -- Alcohol Swabs

-- -- Order 66: Lab chemicals order
-- (9, 15, 8.0, 66, 12.0000, 20.0, NULL),   -- Liver Reagents
-- (9, 8, 8.0, 66, 25.0000, 25.0, NULL),    -- Thyroid Kits
-- (9, 20, 8.0, 66, 2.2500, 30.0, NULL),    -- Test Strips

-- -- Order 67: Dental monthly supply
-- (8, 40, 18.0, 67, 4.5000, 20.0, NULL),   -- Dental Paste
-- (8, 60, 18.0, 67, 2.7500, 15.0, NULL),   -- Prophy Angles
-- (8, 80, 18.0, 67, 1.2500, 10.0, NULL),   -- Sensor Covers

-- -- Order 68: Vaccination campaign
-- (9, 200, 5.0, 68, 18.0000, 40.0, NULL),  -- Flu Vaccines
-- (8, 250, 5.0, 68, 0.8500, 35.0, NULL),   -- Syringes
-- (10, 15, 5.0, 68, 3.5000, 25.0, NULL);



-- Insert dummy data for invoice table
-- INSERT INTO `gluttex`.`invoice` (
--   `invoice_cart_id`,
--   `invoice_number`,
--   `invoice_total_amount`,
--   `invoice_status`,
--   `invoice_issue_date`,
--   `invoice_due_date`,
--   `invoice_notes`
-- ) VALUES
-- -- Cart 1: Blood tests (Paid)
-- (1, 'INV-2024-001', 85.5000, 'paid', '2024-01-15', '2024-02-15', 'Complete blood work invoice - includes CBC, Lipid Profile, Glucose Test'),

-- -- Cart 2: Follow-up tests (Paid)
-- (2, 'INV-2024-002', 120.0000, 'paid', '2024-01-16', '2024-02-16', 'Follow-up liver and thyroid function tests'),

-- -- Cart 3: Family blood work (Paid)
-- (3, 'INV-2024-003', 220.7500, 'paid', '2024-01-17', '2024-02-17', 'Family blood tests package - 2 persons'),

-- -- Cart 4: Annual tests (Paid)
-- (4, 'INV-2024-004', 95.2500, 'paid', '2024-01-18', '2024-02-18', 'Annual health screening tests'),

-- -- Cart 5: Basic tests (Paid)
-- (5, 'INV-2024-005', 65.0000, 'paid', '2024-01-19', '2024-02-19', 'Basic CBC and glucose screening'),

-- -- Cart 6: Imaging - X-ray & Ultrasound (Paid)
-- (6, 'INV-2024-006', 180.5000, 'paid', '2024-01-20', '2024-02-20', 'Chest X-ray and abdominal ultrasound'),

-- -- Cart 7: Advanced imaging (Paid)
-- (7, 'INV-2024-007', 420.5000, 'paid', '2024-01-21', '2024-02-21', 'Brain MRI and CT scan package'),

-- -- Cart 8: Pre-employment screening (Paid)
-- (8, 'INV-2024-008', 150.0000, 'paid', '2024-01-22', '2024-02-22', 'Pre-employment medical tests'),

-- -- Cart 9: Neurological assessment (Paid)
-- (9, 'INV-2024-009', 280.0000, 'paid', '2024-01-23', '2024-02-23', 'Neurological MRI scan'),

-- -- Cart 10: Lung assessment (Paid)
-- (10, 'INV-2024-010', 240.0000, 'paid', '2024-01-24', '2024-02-24', 'CT scan for lung nodule follow-up'),

-- -- Cart 11: Vaccinations (Paid)
-- (11, 'INV-2024-011', 25.0000, 'paid', '2024-01-25', '2024-02-25', 'Annual flu vaccination'),

-- -- Cart 12: Travel vaccinations (Paid)
-- (12, 'INV-2024-012', 300.0000, 'paid', '2024-01-26', '2024-02-26', 'Travel vaccination package'),

-- -- Cart 13: Family vaccinations (Paid)
-- (13, 'INV-2024-013', 50.0000, 'paid', '2024-01-27', '2024-02-27', 'Family flu shots'),

-- -- Cart 14: Business travel (Paid)
-- (14, 'INV-2024-014', 120.0000, 'paid', '2024-01-28', '2024-02-28', 'Business travel vaccinations'),

-- -- Cart 15: HPV vaccination (Paid)
-- (15, 'INV-2024-015', 540.0000, 'paid', '2024-01-29', '2024-02-29', 'Complete HPV vaccination series (3 doses)'),

-- -- Cart 16: Executive health (Paid)
-- (16, 'INV-2024-016', 480.0000, 'paid', '2024-01-30', '2024-03-01', 'Executive health screening package'),

-- -- Cart 17: Annual physical (Unpaid)
-- (17, 'INV-2024-017', 280.0000, 'unpaid', '2024-02-01', '2024-03-01', 'Annual physical exam + elderly parent assessment'),

-- -- Cart 18: Corporate executive (Paid)
-- (18, 'INV-2024-018', 400.0000, 'paid', '2024-02-02', '2024-03-02', 'Corporate executive health checkup'),

-- -- Cart 19: Family physicals (Unpaid)
-- (19, 'INV-2024-019', 160.0000, 'unpaid', '2024-02-03', '2024-03-03', 'Family physical examinations (2 persons)'),

-- -- Cart 20: Geriatric assessment (Paid)
-- (20, 'INV-2024-020', 200.0000, 'paid', '2024-02-04', '2024-03-04', 'Geriatric health assessment'),

-- -- Cart 21: Dental cleaning (Paid)
-- (21, 'INV-2024-021', 105.0000, 'paid', '2024-02-05', '2024-03-05', 'Teeth cleaning with X-rays'),

-- -- Cart 22: Dental fillings (Paid)
-- (22, 'INV-2024-022', 265.0000, 'paid', '2024-02-06', '2024-03-06', 'Two dental fillings with cleaning'),

-- -- Cart 23: Routine dental X-rays (Paid)
-- (23, 'INV-2024-023', 40.0000, 'paid', '2024-02-07', '2024-03-07', 'Routine dental X-rays'),

-- -- Cart 24: 6-month cleaning (Paid)
-- (24, 'INV-2024-024', 65.0000, 'paid', '2024-02-08', '2024-03-08', '6-month dental cleaning'),

-- -- Cart 25: Single filling (Unpaid)
-- (25, 'INV-2024-025', 100.0000, 'unpaid', '2024-02-09', '2024-03-09', 'Single cavity filling'),

-- -- Cart 26: Pathology tests (Paid)
-- (26, 'INV-2024-026', 205.0000, 'paid', '2024-02-10', '2024-03-10', 'Skin biopsy and pap smear tests'),

-- -- Cart 27: Mole biopsy (Paid)
-- (27, 'INV-2024-027', 160.0000, 'paid', '2024-02-11', '2024-03-11', 'Mole biopsy analysis'),

-- -- Cart 28: Gynecological screening (Paid)
-- (28, 'INV-2024-028', 45.0000, 'paid', '2024-02-12', '2024-03-12', 'Annual gynecological pap smear'),

-- -- Cart 29: UTI tests (Paid)
-- (29, 'INV-2024-029', 56.0000, 'paid', '2024-02-13', '2024-03-13', 'Urinalysis and urine culture for UTI'),

-- -- Cart 30: Drug screening (Unpaid)
-- (30, 'INV-2024-030', 20.0000, 'unpaid', '2024-02-14', '2024-03-14', 'Pre-employment drug screening'),

-- -- Cart 31: Allergy testing (Paid)
-- (31, 'INV-2024-031', 270.0000, 'paid', '2024-02-15', '2024-03-15', 'Allergy skin testing and food panel'),

-- -- Cart 32: Genetic testing (Paid)
-- (32, 'INV-2024-032', 379.0000, 'paid', '2024-02-16', '2024-03-16', 'Genetic carrier screening and ancestry test'),

-- -- Cart 33: Physiotherapy (Unpaid)
-- (33, 'INV-2024-033', 255.0000, 'unpaid', '2024-02-17', '2024-03-17', 'Physiotherapy assessment + 3 massage sessions'),

-- -- Cart 34: Nutrition & weight (Paid)
-- (34, 'INV-2024-034', 585.0000, 'paid', '2024-02-18', '2024-03-18', 'Nutrition consultation + weight management program'),

-- -- Cart 35: Therapy package (Unpaid)
-- (35, 'INV-2024-035', 530.0000, 'unpaid', '2024-02-19', '2024-03-19', '4 therapy sessions + couples counseling'),

-- -- Cart 36: Acupuncture (Paid)
-- (36, 'INV-2024-036', 215.0000, 'paid', '2024-02-20', '2024-03-20', '2 acupuncture sessions + electro-acupuncture'),

-- -- Cart 37: Prenatal care (Paid)
-- (37, 'INV-2024-037', 280.0000, 'paid', '2024-02-21', '2024-03-21', 'First trimester ultrasound + prenatal blood work'),

-- -- Cart 38: Pediatric care (Paid)
-- (38, 'INV-2024-038', 165.0000, 'paid', '2024-02-22', '2024-03-22', 'Well-baby checkup + child development assessment'),

-- -- Cart 39: Geriatric care (Unpaid)
-- (39, 'INV-2024-039', 215.0000, 'unpaid', '2024-02-23', '2024-03-23', 'Geriatric assessment + fall risk evaluation'),

-- -- Cart 40: Sports medicine (Paid)
-- (40, 'INV-2024-040', 230.0000, 'paid', '2024-02-24', '2024-03-24', 'Sports injury evaluation + performance consultation'),

-- -- Cart 41: Single tests (Paid)
-- (41, 'INV-2024-041', 45.0000, 'paid', '2024-02-25', '2024-03-25', 'Single blood test + flu shot'),

-- -- Cart 42: Dental + flu (Canceled)
-- (42, 'INV-2024-042', 130.0000, 'canceled', '2024-02-26', '2024-03-26', 'Dental cleaning with X-rays + flu vaccination - Patient canceled');


-- More invoices for comprehensive coverage
-- INSERT INTO `gluttex`.`invoice` (
--   `invoice_cart_id`,
--   `invoice_number`,
--   `invoice_total_amount`,
--   `invoice_status`,
--   `invoice_issue_date`,
--   `invoice_due_date`,
--   `invoice_notes`
-- ) VALUES
-- -- Past due invoices
-- (17, 'INV-2024-043', 280.0000, 'unpaid', '2024-01-15', '2024-02-15', 'PAST DUE - Annual physical exam'),
-- (19, 'INV-2024-044', 160.0000, 'unpaid', '2024-01-20', '2024-02-20', 'PAST DUE - Family physical exams'),
-- (25, 'INV-2024-045', 100.0000, 'unpaid', '2024-01-25', '2024-02-25', 'PAST DUE - Dental filling'),

-- -- Partially paid invoices (treated as unpaid since status is binary)
-- (30, 'INV-2024-046', 20.0000, 'unpaid', '2024-02-10', '2024-03-10', 'Partially paid - balance due $5.00'),
-- (33, 'INV-2024-047', 255.0000, 'unpaid', '2024-02-12', '2024-03-12', 'Payment plan arranged - first payment received'),

-- -- Bulk/wholesale invoices
-- (5, 'INV-2024-048', 650.0000, 'paid', '2024-02-01', '2024-03-01', 'Corporate bulk order - 10 employee screenings'),
-- (11, 'INV-2024-049', 250.0000, 'paid', '2024-02-05', '2024-03-05', 'Company flu vaccination program - 10 employees'),

-- -- Insurance pending invoices
-- (35, 'INV-2024-050', 530.0000, 'unpaid', '2024-02-15', '2024-03-15', 'Awaiting insurance approval'),
-- (39, 'INV-2024-051', 215.0000, 'unpaid', '2024-02-18', '2024-03-18', 'Insurance claim submitted'),

-- -- Zero amount invoices (free services)
-- (11, 'INV-2024-052', 0.0000, 'paid', '2024-02-20', '2024-03-20', 'Free COVID-19 vaccination - government funded'),

-- -- Refunded invoices (canceled status)
-- (42, 'INV-2024-053', 130.0000, 'canceled', '2024-02-22', '2024-03-22', 'Refund issued - patient switched providers'),

-- -- Recent invoices (current month)
-- (17, 'INV-2024-054', 280.0000, 'unpaid', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 30 DAY), 'Current month invoice - sent today'),
-- (25, 'INV-2024-055', 100.0000, 'unpaid', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 30 DAY), 'Current dental work invoice'),

-- -- Overdue invoices (more than 30 days past due)
-- (30, 'INV-2024-056', 20.0000, 'unpaid', '2023-12-15', '2024-01-15', 'OVERDUE - 60+ days past due'),
-- (33, 'INV-2024-057', 255.0000, 'unpaid', '2023-12-20', '2024-01-20', 'OVERDUE - Collections notified'),

-- -- Quarterly invoices
-- (16, 'INV-2024-058', 1440.0000, 'paid', '2024-01-01', '2024-01-31', 'Q1 Corporate executive health package - 3 employees'),
-- (16, 'INV-2024-059', 1440.0000, 'paid', '2024-04-01', '2024-04-30', 'Q2 Corporate executive health package'),
-- (16, 'INV-2024-060', 1440.0000, 'unpaid', '2024-07-01', '2024-07-31', 'Q3 Corporate executive health package - pending');

-- First, create payments (some with invoice references)
-- INSERT INTO `gluttex`.`payment` (
--   `payment_invoice_id`,
--   `payment_amount`,
--   `payment_method`,
--   `payment_status`,
--   `payment_reference`,
--   `payment_notes`
-- ) VALUES
-- -- Full payments for invoices
-- (1, 85.5000, 'card', 'completed', 'TXN-00123456', 'Credit card payment - Visa ending 4321'),
-- (2, 120.0000, 'bank', 'completed', 'BANK-78901234', 'Bank transfer - Ref: INV-2024-002'),
-- (3, 220.7500, 'card', 'completed', 'TXN-56789012', 'Debit card payment - Mastercard'),
-- (4, 95.2500, 'mobile', 'completed', 'MOB-34567890', 'Mobile payment via Apple Pay'),
-- (5, 65.0000, 'cash', 'completed', 'CASH-001', 'Cash payment at counter'),
-- (6, 180.5000, 'card', 'completed', 'TXN-90123456', 'Credit card payment - Amex'),
-- (7, 420.5000, 'bank', 'completed', 'BANK-12345678', 'Corporate bank transfer'),
-- (8, 150.0000, 'card', 'completed', 'TXN-23456789', 'Debit card - company account'),
-- (9, 280.0000, 'bank', 'completed', 'BANK-87654321', 'Insurance direct deposit'),
-- (10, 240.0000, 'card', 'completed', 'TXN-34567890', 'Health savings account card'),

-- -- Partial payments (for unpaid invoices)
-- (17, 140.0000, 'card', 'completed', 'TXN-45678901', 'Partial payment - 50% of total'),
-- (19, 80.0000, 'cash', 'completed', 'CASH-002', 'Partial cash payment - family discount'),
-- (25, 50.0000, 'bank', 'completed', 'BANK-23456789', 'Deposit for dental work'),

-- -- Payments for other invoices
-- (11, 25.0000, 'card', 'completed', 'TXN-56789012', 'Flu shot payment'),
-- (12, 300.0000, 'bank', 'completed', 'BANK-34567890', 'Travel clinic payment'),
-- (13, 50.0000, 'mobile', 'completed', 'MOB-45678901', 'Family vaccination mobile payment'),
-- (14, 120.0000, 'card', 'completed', 'TXN-67890123', 'Business expense card'),
-- (15, 180.0000, 'bank', 'completed', 'BANK-45678901', 'First dose HPV vaccine payment'),
-- (16, 480.0000, 'bank', 'completed', 'BANK-56789012', 'Corporate executive package'),

-- -- More payments with different statuses
-- (20, 200.0000, 'card', 'completed', 'TXN-78901234', 'Geriatric assessment - senior discount applied'),
-- (21, 105.0000, 'cash', 'completed', 'CASH-003', 'Dental cleaning payment'),
-- (22, 265.0000, 'card', 'completed', 'TXN-89012345', 'Dental fillings - insurance co-pay'),
-- (23, 40.0000, 'mobile', 'completed', 'MOB-56789012', 'Dental X-ray mobile payment'),
-- (24, 65.0000, 'card', 'completed', 'TXN-90123456', 'Regular cleaning payment'),

-- -- Failed/refunded payments
-- (42, 130.0000, 'card', 'refunded', 'TXN-REF-12345', 'Refund processed - patient canceled'),
-- (NULL, 45.0000, 'card', 'failed', 'TXN-FAIL-001', 'Payment declined - insufficient funds'),
-- (NULL, 100.0000, 'bank', 'pending', 'BANK-PEND-001', 'Bank transfer initiated - pending confirmation'),

-- -- Payments without invoice reference (direct cart payments)
-- (NULL, 75.0000, 'cash', 'completed', 'CASH-004', 'Direct payment for consultation'),
-- (NULL, 120.0000, 'card', 'completed', 'TXN-01234567', 'Direct card payment for tests'),
-- (NULL, 200.0000, 'bank', 'completed', 'BANK-67890123', 'Direct bank transfer for services');

-- -- Now create receipts (some with payment references, some without)
-- INSERT INTO `gluttex`.`receipt` (
--   `receipt_payment_id`,
--   `receipt_number`,
--   `receipt_amount`,
--   `receipt_notes`,
--   `receipt_cart_ref`
-- ) VALUES
-- -- Receipts with payment references (full payments)
-- (1, 'RCPT-2024-001', 85.5000, 'Receipt for blood work payment - Card TXN-00123456', 1),
-- (2, 'RCPT-2024-002', 120.0000, 'Receipt for follow-up tests - Bank transfer', 2),
-- (3, 'RCPT-2024-003', 220.7500, 'Family blood tests receipt - Paid in full', 3),
-- (4, 'RCPT-2024-004', 95.2500, 'Annual screening receipt - Mobile payment', 4),
-- (5, 'RCPT-2024-005', 65.0000, 'Basic tests receipt - Cash payment', 5),

-- -- Receipts for partial payments
-- (11, 'RCPT-2024-011', 140.0000, 'Partial payment receipt - Balance due: $140.00', 17),
-- (12, 'RCPT-2024-012', 80.0000, 'Family discount applied - Balance: $80.00', 19),
-- (13, 'RCPT-2024-013', 50.0000, 'Dental deposit receipt - Balance due: $50.00', 25),

-- -- Receipts without payment references (cash receipts)
-- (NULL, 'RCPT-2024-021', 180.5000, 'Cash receipt for imaging services - No payment record', 6),
-- (NULL, 'RCPT-2024-022', 420.5000, 'Receipt for advanced imaging - Paid by check', 7),
-- (NULL, 'RCPT-2024-023', 150.0000, 'Pre-employment screening receipt', 8),

-- -- More receipts with payments
-- (6, 'RCPT-2024-024', 180.5000, 'Imaging services - Card payment', 6),
-- (7, 'RCPT-2024-025', 420.5000, 'Advanced imaging - Corporate payment', 7),
-- (8, 'RCPT-2024-026', 150.0000, 'Pre-employment screening - Company card', 8),

-- -- Receipts for other services
-- (9, 'RCPT-2024-027', 280.0000, 'MRI scan receipt - Insurance covered', 9),
-- (10, 'RCPT-2024-028', 240.0000, 'CT scan receipt - HSA payment', 10),
-- (14, 'RCPT-2024-029', 120.0000, 'Travel clinic receipt - Business expense', 14),

-- -- Refund receipt
-- (22, 'RCPT-2024-030', 130.0000, 'REFUND RECEIPT - Services canceled', 42),

-- -- Direct cart receipts (no payment reference)
-- (NULL, 'RCPT-2024-031', 25.0000, 'Flu shot receipt - Paid at clinic', 11),
-- (NULL, 'RCPT-2024-032', 300.0000, 'Travel vaccinations receipt', 12),
-- (NULL, 'RCPT-2024-033', 50.0000, 'Family vaccinations receipt', 13);


-- -- Now create deposits (some with receipts, some without)
-- INSERT INTO `gluttex`.`deposit` (
--   `deposit_cart_id`,
--   `deposit_invoice_id`,
--   `deposit_amount`,
--   `deposit_method`,
--   `deposit_reference`,
--   `deposit_notes`,
--   `deposit_receipt_id`
-- ) VALUES

-- -- Deposits with receipts (full payment scenario)
-- (1, 1, 85.5000, 'card', 'DEP-TXN-001', 'Full deposit for blood work', 1),
-- (2, 2, 120.0000, 'bank', 'DEP-BANK-001', 'Full deposit for follow-up tests', 2),
-- (3, 3, 220.7500, 'card', 'DEP-TXN-002', 'Full deposit for family tests', 3),
-- -- Partial deposits (for unpaid invoices)
-- (17, 17, 140.0000, 'card', 'DEP-TXN-003', '50% deposit for annual physical', 11),
-- (19, 19, 80.0000, 'cash', 'DEP-CASH-001', '50% deposit for family exams', 12),
-- (25, 25, 50.0000, 'bank', 'DEP-BANK-002', '50% deposit for dental work', 13),





-- -- Deposits without receipts
-- (6, 6, 90.2500, 'cash', 'DEP-CASH-002', '50% deposit for imaging services', NULL),
-- (7, 7, 210.2500, 'bank', 'DEP-BANK-003', '50% deposit for advanced imaging', NULL),
-- (33, 33, 127.5000, 'card', 'DEP-TXN-004', '50% deposit for physiotherapy', NULL),

-- -- Deposits for future services (no invoice yet)
-- (35, NULL, 265.0000, 'card', 'DEP-TXN-005', 'Advance deposit for therapy package', NULL),
-- (39, NULL, 107.5000, 'cash', 'DEP-CASH-003', 'Deposit for geriatric assessment', NULL),

-- -- Multiple deposits for same cart/invoice
-- (16, 16, 240.0000, 'bank', 'DEP-BANK-004', 'First deposit for executive package', NULL),
-- (16, 16, 240.0000, 'bank', 'DEP-BANK-005', 'Second deposit for executive package', NULL);


-- -- Deposit with receipt but no invoice (direct service booking)
-- (22, NULL, 132.5000, 'card', 'DEP-TXN-006', 'Deposit for dental fillings', 21),
-- (21, NULL, 135.0000, 'bank', 'DEP-BANK-006', 'Deposit for allergy testing', NULL),

-- -- Small deposits
-- (11, 11, 12.5000, 'cash', 'DEP-CASH-004', 'Token deposit for flu shot', NULL),
-- (23, 23, 20.0000, 'mobile', 'DEP-MOB-001', 'Deposit for dental X-rays', NULL),

-- -- Large/corporate deposits
-- (16, 16, 480.0000, 'bank', 'DEP-BANK-007', 'Corporate bulk deposit - 10 employees', NULL),
-- (34, 34, 292.5000, 'bank', 'DEP-BANK-008', '50% deposit for weight management program', NULL),

-- -- Refunded deposit
-- (42, 42, 130.0000, 'card', 'DEP-REF-001', 'DEPOSIT REFUNDED - Services canceled', 20),

-- -- Recent deposits
-- (17, 17, 70.0000, 'card', 'DEP-TXN-007', 'Additional deposit for balance', NULL),
-- (25, 25, 25.0000, 'cash', 'DEP-CASH-005', 'Additional dental deposit', NULL),

-- -- Deposit without cart reference
-- (NULL, 20, 100.0000, 'bank', 'DEP-BANK-009', 'Deposit against invoice - cart not specified', NULL),
-- (NULL, 21, 52.5000, 'card', 'DEP-TXN-008', 'Partial deposit - cart unknown', NULL);

select * from app_user;
desc app_user ;
insert into app_user (id_app_user,
app_user_name,
app_user_password,
app_user_type,
app_user_preferences,
app_user_image_url,
app_user_last_active,
app_user_last_updated,
app_user_creation)
values
(4, 'admin', '77b23d5396b51608e7189cf8895bd283c88639db5ed6211fa8bfbaecf477409f',  "admin",NULL , NULL , '2025-12-10 08:01:27', '2025-12-10 08:01:27', '2025-12-10 08:01:27' );


INSERT INTO `gluttex`.`management_rule` (
  `rule_ref_org`,
  `rule_ref_provider`,
  `rule_ref_user`,
  `management_rule_code`,
  `management_rule_status`,
  `management_rule_expiry`
) VALUES
-- Provider 1: Magasin habibou sans gluten (Bakery)
(NULL, 1, 4, 63, 'PENDING', DATE_ADD(NOW(), INTERVAL 30 DAY)),

-- Provider 2: Uno (Supermarket)
(NULL, 2, 4, 63, 'ACTIVE', DATE_ADD(NOW(), INTERVAL 60 DAY)),

-- Provider 3: Superette université (Supermarket)
(NULL, 3, 4, 63, 'PENDING', DATE_ADD(NOW(), INTERVAL 45 DAY)),

-- Provider 4: Corridors Shopping (Restaurant)
(NULL, 4, 4, 63, 'REJECTED', DATE_ADD(NOW(), INTERVAL 90 DAY)),

-- Provider 5: Caramel sans gluten (Supermarket)
(NULL, 5, 4, 63, 'SUSPENDED', DATE_ADD(NOW(), INTERVAL 15 DAY)),

-- Provider 6: Magasin habibou sans gluten (Bakery - duplicate name but different ID)
(NULL, 6, 4, 63, 'ACTIVE', DATE_ADD(NOW(), INTERVAL 180 DAY)),

-- Provider 7: Uno (Supermarket - duplicate name but different ID)
(NULL, 7, 4, 63, 'OBSOLETE', DATE_ADD(NOW(), INTERVAL 7 DAY));

-- Optional: Insert more variations with different statuses for testing
INSERT INTO `gluttex`.`management_rule` (
  `rule_ref_org`,
  `rule_ref_provider`,
  `rule_ref_user`,
  `management_rule_code`,
  `management_rule_status`,
  `management_rule_expiry`
) VALUES
-- Additional rules with different expiry dates
(NULL, 1, 4, 63, 'ACTIVE', DATE_ADD(NOW(), INTERVAL 365 DAY)),  -- 1 year expiry
(NULL, 2, 4, 63, 'PENDING', NULL),  -- No expiry date
(NULL, 3, 4, 63, 'ACTIVE', DATE_ADD(NOW(), INTERVAL -7 DAY)),  -- Already expired
(NULL, 4, 4, 63, 'SUSPENDED', DATE_ADD(NOW(), INTERVAL 30 DAY)),

-- Same provider, different rule codes for user 4
(NULL, 2, 4, 64, 'ACTIVE', DATE_ADD(NOW(), INTERVAL 90 DAY)),  -- Different rule code
(NULL, 2, 4, 65, 'PENDING', DATE_ADD(NOW(), INTERVAL 30 DAY)),  -- Another rule code

-- Same provider and rule code, different users (if you want to test with other users)
(NULL, 2, 1, 63, 'ACTIVE', DATE_ADD(NOW(), INTERVAL 60 DAY)),  -- User ID 1
(NULL, 2, 2, 63, 'ACTIVE', DATE_ADD(NOW(), INTERVAL 60 DAY)),  -- User ID 2
(NULL, 2, 3, 63, 'ACTIVE', DATE_ADD(NOW(), INTERVAL 60 DAY));  -- User ID 3

-- -----------------------------------------------------
-- View `gluttex`.`business_operation`
-- -----------------------------------------------------
DROP VIEW IF EXISTS `gluttex`.`business_operation`;

CREATE OR REPLACE VIEW `gluttex`.`financial_documents_status` AS
-- PART 1: Invoice-based transactions (keep as is)
SELECT 
    -- Document Identification
    'invoice' AS document_type,
    i.invoice_id AS document_id,
    i.invoice_number AS document_number,
    
    -- Transaction Identification
    COALESCE(c.cart_id, po.id_placed_order) AS source_id,
    CASE 
        WHEN c.cart_id IS NOT NULL THEN 'cart_based'
        WHEN po.id_placed_order IS NOT NULL THEN 'order_based'
        ELSE 'direct_invoice'
    END AS source_type,
    
    -- Provider/Supplier Information
    COALESCE(
        pp_cart.id_product_provider,
        (SELECT pp_prod.id_product_provider 
         FROM ordered_item oi2 
         JOIN product p2 ON oi2.ordered_product_id = p2.id_product
         JOIN product_provider pp_prod ON p2.product_provider_id = pp_prod.id_product_provider
         WHERE oi2.order_ref = po.id_placed_order 
         LIMIT 1),
        0
    ) AS supplier_id,
    
    -- Customer Information with TYPE
    COALESCE(
        c.cart_client_user,
        po.ordering_user_id,
        NULL
    ) AS customer_id,
    
    -- CUSTOMER TYPE: Determine if customer is user or person
    CASE 
        -- If customer_id exists in app_user table, it's a user
        WHEN COALESCE(c.cart_client_user, po.ordering_user_id) IS NOT NULL 
             AND EXISTS (SELECT 1 FROM app_user au WHERE au.id_app_user = COALESCE(c.cart_client_user, po.ordering_user_id))
            THEN 'user'
        -- If cart has person_ref, it's a person
        WHEN c.cart_person_ref IS NOT NULL 
            THEN 'person'
        -- Check if placed_order has person via ordering_user -> person
        WHEN po.ordering_user_id IS NOT NULL AND EXISTS (
            SELECT 1 FROM app_user au2 
            JOIN person p ON au2.app_user_person_id = p.id_person 
            WHERE au2.id_app_user = po.ordering_user_id
        )
            THEN 'person'
        ELSE 'unknown'
    END AS customer_type,
    
    -- Person ID if available
    COALESCE(
        c.cart_person_ref,
        (SELECT p2.id_person FROM app_user au3 
         JOIN person p2 ON au3.app_user_person_id = p2.id_person 
         WHERE au3.id_app_user = COALESCE(c.cart_client_user, po.ordering_user_id)
         LIMIT 1)
    ) AS customer_person_id,
    
    -- Seller Information
    COALESCE(
        c.cart_selling_user
    ) AS seller_id,
    
    -- Financial Information
    GREATEST(i.invoice_total_amount, 0) AS document_amount,
    i.invoice_issue_date AS issue_date,
    i.invoice_due_date AS due_date,
    
    -- Payment Information
    COALESCE(
        (SELECT SUM(p.payment_amount) 
         FROM payment p 
         WHERE p.payment_invoice_id = i.invoice_id 
         ),
        0
    ) AS total_paid,
    
    -- Deposit Information
    COALESCE(
        (SELECT SUM(d.deposit_amount) 
         FROM deposit d 
         WHERE d.deposit_invoice_id = i.invoice_id),
        0
    ) AS total_deposited,
    
    -- Additional Fees
    COALESCE(
        (SELECT SUM(af.additional_fee_amount) 
         FROM additional_fee af 
         WHERE af.additional_fee_payment_id IN (
             SELECT p2.payment_id 
             FROM payment p2 
             WHERE p2.payment_invoice_id = i.invoice_id
         )),
        0
    ) AS additional_fees,
    
    -- Balance Calculation
    GREATEST(
        i.invoice_total_amount - 
        COALESCE((SELECT SUM(p.payment_amount) FROM payment p WHERE p.payment_invoice_id = i.invoice_id ), 0) -
        COALESCE((SELECT SUM(d.deposit_amount) FROM deposit d WHERE d.deposit_invoice_id = i.invoice_id), 0),
        0
    ) AS outstanding_balance,
    
    -- Status Summary
    i.invoice_status AS document_status,
    
    -- Payment Status Classification (3-STATE MODEL)
    CASE 
        -- Canceled state (special case)
        WHEN i.invoice_status = 'canceled' THEN 'canceled'
        
        -- PAID STATE: Full payment via payments OR deposits
        WHEN (COALESCE((SELECT SUM(p.payment_amount) FROM payment p WHERE p.payment_invoice_id = i.invoice_id ), 0) +
              COALESCE((SELECT SUM(d.deposit_amount) FROM deposit d WHERE d.deposit_invoice_id = i.invoice_id), 0)) >= i.invoice_total_amount 
            THEN 'paid'
        
        -- DEPOSITED STATE: Some payment/deposit made but not full
        WHEN (COALESCE((SELECT SUM(p.payment_amount) FROM payment p WHERE p.payment_invoice_id = i.invoice_id ), 0) +
              COALESCE((SELECT SUM(d.deposit_amount) FROM deposit d WHERE d.deposit_invoice_id = i.invoice_id), 0)) > 0
            THEN 'deposited'
        
        -- UNPAID STATE: No payments or deposits
        ELSE 'unpaid'
    END AS payment_status,
    
    -- Payment method detail (for reference)
    CASE 
        WHEN EXISTS (SELECT 1 FROM payment p WHERE p.payment_invoice_id = i.invoice_id ) 
             AND EXISTS (SELECT 1 FROM deposit d WHERE d.deposit_invoice_id = i.invoice_id AND d.deposit_amount > 0)
            THEN 'mixed_payments'
        WHEN EXISTS (SELECT 1 FROM payment p WHERE p.payment_invoice_id = i.invoice_id )
            THEN 'payment_only'
        WHEN EXISTS (SELECT 1 FROM deposit d WHERE d.deposit_invoice_id = i.invoice_id AND d.deposit_amount > 0)
            THEN 'deposit_only'
        ELSE 'no_payments'
    END AS payment_method,
    
    -- Aging Information
    CASE 
        WHEN i.invoice_issue_date IS NOT NULL THEN 
            DATEDIFF(CURRENT_DATE(), i.invoice_issue_date)
        ELSE 0
    END AS days_issued,
    
    CASE 
        WHEN i.invoice_due_date IS NOT NULL AND i.invoice_due_date < CURRENT_DATE() THEN 
            DATEDIFF(CURRENT_DATE(), i.invoice_due_date)
        ELSE 0
    END AS days_overdue,
    
    -- Metadata
    i.invoice_created_at,
    i.invoice_updated_at

FROM invoice i
LEFT JOIN cart c ON i.invoice_cart_id = c.cart_id
LEFT JOIN placed_order po ON i.invoice_id = po.placed_order_invoice_ref
LEFT JOIN product_provider pp_cart ON c.cart_product_provider_id = pp_cart.id_product_provider

UNION ALL

-- PART 2: Deposit-only transactions (keep as is)
SELECT 
    'deposit' AS document_type,
    d.deposit_id AS document_id,
    CONCAT('DEP-', d.deposit_id) AS document_number,
    
    COALESCE(d.deposit_cart_id, d.deposit_invoice_id) AS source_id,
    CASE 
        WHEN d.deposit_cart_id IS NOT NULL THEN 'cart_based'
        WHEN d.deposit_invoice_id IS NOT NULL THEN 'invoice_based'
        ELSE 'direct_deposit'
    END AS source_type,
    
    COALESCE(
        (SELECT pp.id_product_provider 
         FROM cart c2 
         JOIN product_provider pp ON c2.cart_product_provider_id = pp.id_product_provider
         WHERE c2.cart_id = d.deposit_cart_id),
        (SELECT pp2.id_product_provider 
         FROM invoice i2 
         LEFT JOIN cart c3 ON i2.invoice_cart_id = c3.cart_id
         LEFT JOIN product_provider pp2 ON c3.cart_product_provider_id = pp2.id_product_provider
         WHERE i2.invoice_id = d.deposit_invoice_id),
        0
    ) AS supplier_id,
    
    -- Customer identification with TYPE
    COALESCE(
        (SELECT COALESCE(c4.cart_client_user) 
         FROM cart c4 
         WHERE c4.cart_id = d.deposit_cart_id),
        (SELECT COALESCE(c5.cart_client_user) 
         FROM invoice i3 
         LEFT JOIN cart c5 ON i3.invoice_cart_id = c5.cart_id
         WHERE i3.invoice_id = d.deposit_invoice_id),
        NULL
    ) AS customer_id,
    
    -- CUSTOMER TYPE for deposits
    CASE 
        -- If from cart with cart_client_user
        WHEN d.deposit_cart_id IS NOT NULL AND EXISTS (
            SELECT 1 FROM cart c6 
            WHERE c6.cart_id = d.deposit_cart_id 
            AND c6.cart_client_user IS NOT NULL 
            AND EXISTS (SELECT 1 FROM app_user au WHERE au.id_app_user = c6.cart_client_user)
        ) THEN 'user'
        
        -- If from cart with cart_person_ref
        WHEN d.deposit_cart_id IS NOT NULL AND EXISTS (
            SELECT 1 FROM cart c7 WHERE c7.cart_id = d.deposit_cart_id AND c7.cart_person_ref IS NOT NULL
        ) THEN 'person'
        
        -- If from invoice, check the associated cart
        WHEN d.deposit_invoice_id IS NOT NULL THEN
            CASE 
                WHEN EXISTS (
                    SELECT 1 FROM invoice i4 
                    LEFT JOIN cart c8 ON i4.invoice_cart_id = c8.cart_id
                    WHERE i4.invoice_id = d.deposit_invoice_id 
                    AND c8.cart_client_user IS NOT NULL
                    AND EXISTS (SELECT 1 FROM app_user au2 WHERE au2.id_app_user = c8.cart_client_user)
                ) THEN 'user'
                WHEN EXISTS (
                    SELECT 1 FROM invoice i5 
                    LEFT JOIN cart c9 ON i5.invoice_cart_id = c9.cart_id
                    WHERE i5.invoice_id = d.deposit_invoice_id 
                    AND c9.cart_person_ref IS NOT NULL
                ) THEN 'person'
                ELSE 'unknown'
            END
        ELSE 'unknown'
    END AS customer_type,
    
    -- Person ID for deposits
    COALESCE(
        (SELECT c10.cart_person_ref FROM cart c10 WHERE c10.cart_id = d.deposit_cart_id),
        (SELECT c11.cart_person_ref FROM invoice i6 
         LEFT JOIN cart c11 ON i6.invoice_cart_id = c11.cart_id
         WHERE i6.invoice_id = d.deposit_invoice_id),
        0
    ) AS customer_person_id,
    
    -- Seller identification
    COALESCE(
        (SELECT COALESCE(c12.cart_selling_user) 
         FROM cart c12 
         WHERE c12.cart_id = d.deposit_cart_id),
        (SELECT COALESCE(c13.cart_selling_user) 
         FROM invoice i7 
         LEFT JOIN cart c13 ON i7.invoice_cart_id = c13.cart_id
         WHERE i7.invoice_id = d.deposit_invoice_id),
        0
    ) AS seller_id,
    
    d.deposit_amount AS document_amount,
    DATE(d.deposit_created_at) AS issue_date,
    DATE(d.deposit_created_at) AS due_date,
    
    0 AS total_paid,
    d.deposit_amount AS total_deposited,
    
    0 AS additional_fees,
    
    -- Balance calculation
    CASE 
        WHEN d.deposit_invoice_id IS NOT NULL THEN
            GREATEST(
                (SELECT i8.invoice_total_amount 
                 FROM invoice i8 
                 WHERE i8.invoice_id = d.deposit_invoice_id) - 
                d.deposit_amount -
                COALESCE((SELECT SUM(p.payment_amount) FROM payment p WHERE p.payment_invoice_id = d.deposit_invoice_id ), 0),
                0
            )
        ELSE d.deposit_amount
    END AS outstanding_balance,
    
    'pending' AS document_status,
    
    -- Payment Status (3-STATE MODEL for deposits)
    CASE 
        WHEN d.deposit_invoice_id IS NOT NULL THEN
            CASE 
                -- PAID STATE: Deposit covers full invoice amount
                WHEN d.deposit_amount >= 
                    (SELECT i9.invoice_total_amount 
                     FROM invoice i9 
                     WHERE i9.invoice_id = d.deposit_invoice_id)
                    THEN 'paid'
                -- DEPOSITED STATE: Partial deposit
                WHEN d.deposit_amount > 0 THEN 'deposited'
                ELSE 'unpaid'
            END
        -- Cart deposit (no invoice yet)
        ELSE CASE
            WHEN d.deposit_amount > 0 THEN 'deposited'
            ELSE 'unpaid'
        END
    END AS payment_status,
    
    -- Payment method detail
    'deposit_only' AS payment_method,
    
    CASE 
        WHEN d.deposit_created_at IS NOT NULL THEN 
            DATEDIFF(CURRENT_DATE(), d.deposit_created_at)
        ELSE 0
    END AS days_issued,
    0 AS days_overdue,
    
    d.deposit_created_at,
    d.deposit_updated_at

FROM deposit d
WHERE d.deposit_amount > 0

UNION ALL

-- PART 3: Cart transactions with payments but no invoice (NEW - FIXED)
SELECT 
    'cart_with_payments' AS document_type,  -- Changed from 'pending_cart'
    c.cart_id AS document_id,
    CONCAT('CART-', c.cart_id) AS document_number,
    
    c.cart_id AS source_id,
    'cart_based' AS source_type,
    
    pp.id_product_provider AS supplier_id,
    
    COALESCE(c.cart_client_user, NULL) AS customer_id,
    
    -- CUSTOMER TYPE for carts
    CASE 
        WHEN COALESCE(c.cart_client_user) IS NOT NULL 
             AND EXISTS (SELECT 1 FROM app_user au WHERE au.id_app_user = COALESCE(c.cart_client_user))
            THEN 'user'
        WHEN c.cart_person_ref IS NOT NULL 
            THEN 'person'
        ELSE 'unknown'
    END AS customer_type,
    
    COALESCE(c.cart_person_ref, 0) AS customer_person_id,
    
    COALESCE(c.cart_selling_user, 0) AS seller_id,
    
    c.cart_total_amount AS document_amount,
    DATE(c.cart_created_at) AS issue_date,
    COALESCE(c.cart_due_date, DATE_ADD(c.cart_created_at, INTERVAL 30 DAY)) AS due_date,
    
    -- CALCULATE PAYMENTS: Check if cart has payments via receipts
    COALESCE(
        (SELECT SUM(r.receipt_amount)
         FROM receipt r 
         WHERE r.receipt_cart_ref = c.cart_id),
        0
    ) AS total_paid,
    
    -- CALCULATE DEPOSITS
    COALESCE(
        (SELECT SUM(d2.deposit_amount) 
         FROM deposit d2 
         WHERE d2.deposit_cart_id = c.cart_id),
        0
    ) AS total_deposited,
    
    0 AS additional_fees,
    
    -- Balance calculation: cart total - payments - deposits
    GREATEST(
        c.cart_total_amount - 
        COALESCE((SELECT SUM(r.receipt_amount) FROM receipt r WHERE r.receipt_cart_ref = c.cart_id), 0) -
        COALESCE((SELECT SUM(d2.deposit_amount) FROM deposit d2 WHERE d2.deposit_cart_id = c.cart_id), 0),
        0
    ) AS outstanding_balance,
    
    c.cart_status AS document_status,
    
    -- Payment Status (3-STATE MODEL) - IMPROVED LOGIC
    CASE 
        -- Canceled state (special case)
        WHEN c.cart_status = 'canceled' THEN 'canceled'
        
        -- PAID STATE: Payments + Deposits >= Cart total
        WHEN (
            COALESCE((SELECT SUM(r.receipt_amount) FROM receipt r WHERE r.receipt_cart_ref = c.cart_id), 0) +
            COALESCE((SELECT SUM(d2.deposit_amount) FROM deposit d2 WHERE d2.deposit_cart_id = c.cart_id), 0)
        ) >= c.cart_total_amount 
            THEN 'paid'
        
        -- DEPOSITED STATE: Has any payments or deposits
        WHEN (
            COALESCE((SELECT SUM(r.receipt_amount) FROM receipt r WHERE r.receipt_cart_ref = c.cart_id), 0) +
            COALESCE((SELECT SUM(d2.deposit_amount) FROM deposit d2 WHERE d2.deposit_cart_id = c.cart_id), 0)
        ) > 0
            THEN 'deposited'
        
        -- UNPAID STATE: No payments or deposits
        ELSE 'unpaid'
    END AS payment_status,
    
    -- Payment method detail
    CASE 
        WHEN EXISTS (SELECT 1 FROM receipt r WHERE r.receipt_cart_ref = c.cart_id AND r.receipt_amount > 0)
            AND EXISTS (SELECT 1 FROM deposit d WHERE d.deposit_cart_id = c.cart_id AND d.deposit_amount > 0)
            THEN 'mixed_payments'
        WHEN EXISTS (SELECT 1 FROM receipt r WHERE r.receipt_cart_ref = c.cart_id AND r.receipt_amount > 0)
            THEN 'payment_only'
        WHEN EXISTS (SELECT 1 FROM deposit d WHERE d.deposit_cart_id = c.cart_id AND d.deposit_amount > 0)
            THEN 'deposit_only'
        ELSE 'no_payments'
    END AS payment_method,
    
    DATEDIFF(CURRENT_DATE(), c.cart_created_at) AS days_issued,
    
    -- Calculate days overdue
    CASE 
        WHEN COALESCE(c.cart_due_date, DATE_ADD(c.cart_created_at, INTERVAL 30 DAY)) < CURRENT_DATE() 
             AND (
                COALESCE((SELECT SUM(r.receipt_amount) FROM receipt r WHERE r.receipt_cart_ref = c.cart_id), 0) +
                COALESCE((SELECT SUM(d2.deposit_amount) FROM deposit d2 WHERE d2.deposit_cart_id = c.cart_id), 0)
             ) < c.cart_total_amount
            THEN DATEDIFF(CURRENT_DATE(), COALESCE(c.cart_due_date, DATE_ADD(c.cart_created_at, INTERVAL 30 DAY)))
        ELSE 0
    END AS days_overdue,
    
    c.cart_created_at,
    c.cart_updated_at

FROM cart c
LEFT JOIN product_provider pp ON c.cart_product_provider_id = pp.id_product_provider
WHERE 
    -- Include ALL carts that don't have invoices
    NOT EXISTS (
        SELECT 1 FROM invoice i WHERE i.invoice_cart_id = c.cart_id
    )
    -- But exclude carts that are canceled (unless you want to see them)
    AND c.cart_status != 'canceled'

UNION ALL

-- PART 4: Receipt-only transactions (keep as is)
SELECT 
    'receipt' AS document_type,
    r.receipt_id AS document_id,
    COALESCE(r.receipt_number, CONCAT('REC-', r.receipt_id)) AS document_number,
    
    r.receipt_cart_ref AS source_id,
    CASE 
        WHEN r.receipt_cart_ref IS NOT NULL THEN 'cart_based'
        ELSE 'direct_receipt'
    END AS source_type,
    
    COALESCE(
        (SELECT pp.id_product_provider 
         FROM cart c 
         JOIN product_provider pp ON c.cart_product_provider_id = pp.id_product_provider
         WHERE c.cart_id = r.receipt_cart_ref),
        0
    ) AS supplier_id,
    
    -- Customer information from cart
    COALESCE(
        (SELECT c2.cart_client_user FROM cart c2 WHERE c2.cart_id = r.receipt_cart_ref),
        (SELECT c3.cart_selling_user FROM cart c3 WHERE c3.cart_id = r.receipt_cart_ref),
        NULL
    ) AS customer_id,
    
    -- CUSTOMER TYPE for receipts
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM cart c4 
            WHERE c4.cart_id = r.receipt_cart_ref 
            AND c4.cart_client_user IS NOT NULL
            AND EXISTS (SELECT 1 FROM app_user au WHERE au.id_app_user = c4.cart_client_user)
        ) THEN 'user'
        WHEN EXISTS (
            SELECT 1 FROM cart c5 
            WHERE c5.cart_id = r.receipt_cart_ref 
            AND c5.cart_person_ref IS NOT NULL
        ) THEN 'person'
        WHEN EXISTS (
            SELECT 1 FROM cart c6 
            WHERE c6.cart_id = r.receipt_cart_ref 
            AND c6.cart_selling_user IS NOT NULL
            AND EXISTS (SELECT 1 FROM app_user au2 WHERE au2.id_app_user = c6.cart_selling_user)
        ) THEN 'user'
        ELSE 'unknown'
    END AS customer_type,
    
    -- Person ID from cart
    COALESCE(
        (SELECT c7.cart_person_ref FROM cart c7 WHERE c7.cart_id = r.receipt_cart_ref),
        0
    ) AS customer_person_id,
    
    -- Seller from cart
    COALESCE(
        (SELECT c8.cart_selling_user FROM cart c8 WHERE c8.cart_id = r.receipt_cart_ref),
        0
    ) AS seller_id,
    
    r.receipt_amount AS document_amount,
    r.receipt_created_at AS issue_date,
    r.receipt_created_at AS due_date,
    
    COALESCE(
        (SELECT p.payment_amount 
         FROM payment p 
         WHERE p.payment_id = r.receipt_payment_id 
         ),
        r.receipt_amount
    ) AS total_paid,
    
    0 AS total_deposited,
    
    0 AS additional_fees,
    
    0 AS outstanding_balance, -- Receipts are always fully paid
    
    'completed' AS document_status,
    
    -- Receipts are always PAID
    'paid' AS payment_status,
    
    -- Payment method detail
    COALESCE(
        (SELECT p2.payment_method FROM payment p2 WHERE p2.payment_id = r.receipt_payment_id),
        'cash'
    ) AS payment_method_detail,
    
    CASE 
        WHEN r.receipt_created_at IS NOT NULL THEN 
            DATEDIFF(CURRENT_DATE(), r.receipt_created_at)
        ELSE 0
    END AS days_issued,
    0 AS days_overdue,
    
    r.receipt_created_at,
    DATEDIFF(CURRENT_DATE(), r.receipt_created_at)

FROM receipt r
WHERE r.receipt_amount > 0

-- Optional: Add order by for consistent results
ORDER BY issue_date DESC, document_type, document_id;

CREATE OR REPLACE VIEW business_operation AS
-- PART 1: Cart-based operations with receipts OR invoices
SELECT 
    -- Supplier information
    pp.id_product_provider AS supplier_id,
    
    -- Order information (if exists)
    po.id_placed_order AS order_id,
    
    -- Cart information
    c.cart_id,
    
    -- Client information
    COALESCE(c.cart_client_user, c.cart_selling_user) AS client_id,
    
    -- Seller information
    COALESCE(c.cart_selling_user, c.cart_client_user) AS seller_id,
    
    -- Financial information (use appropriate amount based on document type)
    CASE 
        WHEN i.invoice_id IS NOT NULL THEN i.invoice_total_amount
        WHEN r.receipt_id IS NOT NULL THEN r.receipt_amount
        ELSE c.cart_total_amount
    END AS total_amount,
    
    -- Invoice information (if exists)
    i.invoice_id,
    COALESCE(i.invoice_status, 
        CASE 
            WHEN r.receipt_id IS NOT NULL THEN 'receipt_only'
            ELSE 'no_document'
        END
    ) AS invoice_status,
    
    -- Receipt information (if exists)
    r.receipt_id,
    
    -- Total paid amount (CRITICAL: Check both receipt AND invoice payments)
    COALESCE(
        -- 1. Receipt-based payments (direct receipt_payment_id link)
        (SELECT SUM(p2.payment_amount)
         FROM payment p2
         WHERE p2.payment_id = r.receipt_payment_id
         AND p2.payment_status IN ('completed', 'partial')),
         
        -- 2. Invoice-based payments (invoice_id link)
        (SELECT SUM(p3.payment_amount)
         FROM payment p3
         WHERE p3.payment_invoice_id = i.invoice_id
         AND p3.payment_status IN ('completed', 'partial')),
         
        0
    ) AS total_paid,
    
    -- Total pending payments
    COALESCE(
        (SELECT SUM(p2.payment_amount)
         FROM payment p2
         WHERE p2.payment_id = r.receipt_payment_id
         AND p2.payment_status IN ('pending', 'processing')),
         
        (SELECT SUM(p3.payment_amount)
         FROM payment p3
         WHERE p3.payment_invoice_id = i.invoice_id
         AND p3.payment_status IN ('pending', 'processing')),
         
        0
    ) AS total_pending,
    
    -- Total deposited amount
    COALESCE(
        (SELECT SUM(d2.deposit_amount) 
         FROM deposit d2 
         WHERE d2.deposit_cart_id = c.cart_id
         AND d2.deposit_amount > 0), 
        0
    ) AS total_deposited,
    
    -- Balance due calculation
    CASE 
        WHEN i.invoice_id IS NOT NULL THEN 
            i.invoice_total_amount - 
            COALESCE(
                (SELECT SUM(p3.payment_amount)
                 FROM payment p3
                 WHERE p3.payment_invoice_id = i.invoice_id
                 AND p3.payment_status IN ('completed', 'partial')), 0
            )
        WHEN r.receipt_id IS NOT NULL THEN 
            r.receipt_amount - 
            COALESCE(
                (SELECT SUM(p2.payment_amount)
                 FROM payment p2
                 WHERE p2.payment_id = r.receipt_payment_id
                 AND p2.payment_status IN ('completed', 'partial')), 0
            )
        ELSE c.cart_total_amount
    END AS balance_due,
    
    -- Payment status (comprehensive)
    CASE 
        -- Receipt-based payments (typically completed immediately)
        WHEN r.receipt_id IS NOT NULL THEN
            CASE 
                WHEN EXISTS (
                    SELECT 1 FROM payment p2
                    WHERE p2.payment_id = r.receipt_payment_id
                    AND p2.payment_status = 'completed'
                    AND p2.payment_amount >= r.receipt_amount
                ) THEN 'fully_paid'
                
                WHEN EXISTS (
                    SELECT 1 FROM payment p2
                    WHERE p2.payment_id = r.receipt_payment_id
                    AND p2.payment_status = 'completed'
                ) THEN 'partially_paid_receipt'
                
                ELSE 'receipt_unpaid'
            END
        
        -- Invoice-based payments
        WHEN i.invoice_id IS NOT NULL THEN
            CASE 
                -- Fully paid invoice
                WHEN EXISTS (
                    SELECT 1 FROM payment p3 
                    WHERE p3.payment_invoice_id = i.invoice_id 
                    AND p3.payment_status = 'completed'
                    AND p3.payment_amount >= i.invoice_total_amount
                ) THEN 'fully_paid'
                
                -- Partial payment (completed or partial status)
                WHEN EXISTS (
                    SELECT 1 FROM payment p3 
                    WHERE p3.payment_invoice_id = i.invoice_id 
                    AND p3.payment_status IN ('completed', 'partial')
                    AND p3.payment_amount > 0
                ) THEN 'partially_paid'
                
                -- Pending payments
                WHEN EXISTS (
                    SELECT 1 FROM payment p3 
                    WHERE p3.payment_invoice_id = i.invoice_id 
                    AND p3.payment_status IN ('pending', 'processing')
                ) THEN 'pending_payment'
                
                -- No payments
                ELSE 'unpaid_invoice'
            END
        
        -- No documents yet
        ELSE 'no_document'
    END AS payment_status,
    
    -- Detailed payment status
    CASE 
        WHEN r.receipt_id IS NOT NULL THEN
            COALESCE(
                (SELECT p2.payment_status
                 FROM payment p2
                 WHERE p2.payment_id = r.receipt_payment_id
                 LIMIT 1),
                'receipt_no_payment'
            )
        WHEN i.invoice_id IS NOT NULL THEN
            COALESCE(
                (SELECT p3.payment_status
                 FROM payment p3
                 WHERE p3.payment_invoice_id = i.invoice_id
                 ORDER BY p3.payment_created_at DESC
                 LIMIT 1),
                'invoice_no_payment'
            )
        ELSE 'no_payments'
    END AS detailed_payment_status,
    
    -- Document type
    CASE 
        WHEN i.invoice_id IS NOT NULL AND r.receipt_id IS NOT NULL THEN 'invoice_and_receipt'
        WHEN i.invoice_id IS NOT NULL THEN 'invoice'
        WHEN r.receipt_id IS NOT NULL THEN 'receipt'
        ELSE 'no_document'
    END AS document_type,
    
    -- Operation type (based on cart contents)
    CASE 
        WHEN EXISTS (SELECT 1 FROM ordered_item oi WHERE oi.ordered_item_cart_ref = c.cart_id) 
             AND EXISTS (SELECT 1 FROM ordered_service os WHERE os.ordered_service_cart_id = c.cart_id)
        THEN 'mixed_products_services'
        WHEN EXISTS (SELECT 1 FROM ordered_item oi WHERE oi.ordered_item_cart_ref = c.cart_id) 
        THEN 'products_only'
        WHEN EXISTS (SELECT 1 FROM ordered_service os WHERE os.ordered_service_cart_id = c.cart_id) 
        THEN 'services_only'
        ELSE 'empty_cart'
    END AS operation_type,
    
    -- Payment method
    COALESCE(
        -- From receipt payments
        (SELECT p2.payment_method
         FROM payment p2
         WHERE p2.payment_id = r.receipt_payment_id
         AND p2.payment_status IN ('completed', 'partial')
         LIMIT 1),
         
        -- From invoice payments
        (SELECT p3.payment_method
         FROM payment p3
         WHERE p3.payment_invoice_id = i.invoice_id
         AND p3.payment_status IN ('completed', 'partial')
         ORDER BY p3.payment_created_at DESC
         LIMIT 1),
         
        'not_paid'
    ) AS payment_method,
    
    -- Payment reference
    COALESCE(
        (SELECT p2.payment_reference
         FROM payment p2
         WHERE p2.payment_id = r.receipt_payment_id
         AND p2.payment_status IN ('completed', 'partial')
         LIMIT 1),
         
        (SELECT p3.payment_reference
         FROM payment p3
         WHERE p3.payment_invoice_id = i.invoice_id
         AND p3.payment_status IN ('completed', 'partial')
         ORDER BY p3.payment_created_at DESC
         LIMIT 1),
         
        NULL
    ) AS payment_reference,
    
    -- Source identifier
    'cart_based' AS source_table,
    
    -- Creation timestamp
    COALESCE(
        i.invoice_created_at,
        r.receipt_created_at,
        c.cart_created_at
    ) AS operation_date,
    
    -- Cart status
    c.cart_status

FROM cart c
-- Join to Product Provider
LEFT JOIN product_provider pp ON c.cart_product_provider_id = pp.id_product_provider
-- Join to Invoice (if exists)
LEFT JOIN invoice i ON c.cart_id = i.invoice_cart_id
-- Join to Receipt (if exists)
LEFT JOIN receipt r ON c.cart_id = r.receipt_cart_ref
-- Join to Placed Order (if exists)
LEFT JOIN placed_order po ON (
    po.placed_order_invoice_ref = i.invoice_id 
    OR po.id_placed_order IN (
        SELECT oi.order_ref 
        FROM ordered_item oi 
        WHERE oi.ordered_item_cart_ref = c.cart_id
    )
)

WHERE c.cart_status IN ('completed', 'pending', 'partial')  -- Include partial status

UNION ALL

-- PART 2: Direct Order-based items (without cart reference)
-- [Keep this part similar to before but simplified]
SELECT 
    -- Supplier information
    COALESCE(
        (SELECT pp2.id_product_provider 
         FROM product p2 
         JOIN product_provider pp2 ON p2.product_provider_id = pp2.id_product_provider
         WHERE p2.id_product = oi.ordered_product_id),
        0
    ) AS supplier_id,
    
    oi.order_ref AS order_id,
    
    NULL AS cart_id,
    
    po.ordering_user_id AS client_id,
    
    COALESCE(
        (SELECT au.id_app_user FROM app_user au 
         WHERE au.id_app_user IN (SELECT au2.id_app_user FROM app_user au2 WHERE au2.id_app_user = po.ordering_user_id)),
        po.ordering_user_id
    ) AS seller_id,
    
    (oi.ordered_quantity * oi.unit_price * 
     (1 - COALESCE(oi.product_discount, 0)/100) *
     (1 + COALESCE(oi.applied_vat, 0)/100)) AS total_amount,
    
    i.invoice_id,
    COALESCE(i.invoice_status, 'no_invoice') AS invoice_status,
    
    r.receipt_id,
    
    COALESCE(
        (SELECT SUM(p2.payment_amount)
         FROM payment p2
         WHERE p2.payment_invoice_id = i.invoice_id
         AND p2.payment_status IN ('completed', 'partial')),
        0
    ) AS total_paid,
    
    COALESCE(
        (SELECT SUM(p2.payment_amount)
         FROM payment p2
         WHERE p2.payment_invoice_id = i.invoice_id
         AND p2.payment_status IN ('pending', 'processing')),
        0
    ) AS total_pending,
    
    COALESCE(
        (SELECT SUM(d2.deposit_amount)
         FROM deposit d2
         WHERE d2.deposit_invoice_id = i.invoice_id),
        0
    ) AS total_deposited,
    
    (oi.ordered_quantity * oi.unit_price * 
     (1 - COALESCE(oi.product_discount, 0)/100) *
     (1 + COALESCE(oi.applied_vat, 0)/100)) - 
    COALESCE(
        (SELECT SUM(p2.payment_amount)
         FROM payment p2
         WHERE p2.payment_invoice_id = i.invoice_id
         AND p2.payment_status IN ('completed', 'partial')), 0
    ) AS balance_due,
    
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM payment p2 
            WHERE p2.payment_invoice_id = i.invoice_id 
            AND p2.payment_status = 'completed'
            AND p2.payment_amount >= i.invoice_total_amount
        ) THEN 'fully_paid'
        
        WHEN EXISTS (
            SELECT 1 FROM payment p2 
            WHERE p2.payment_invoice_id = i.invoice_id 
            AND p2.payment_status IN ('completed', 'partial')
            AND p2.payment_amount > 0
        ) THEN 'partially_paid'
        
        WHEN EXISTS (
            SELECT 1 FROM payment p2 
            WHERE p2.payment_invoice_id = i.invoice_id 
            AND p2.payment_status IN ('pending', 'processing')
        ) THEN 'pending_payment'
        
        ELSE 'unpaid'
    END AS payment_status,
    
    COALESCE(
        (SELECT p2.payment_status
         FROM payment p2
         WHERE p2.payment_invoice_id = i.invoice_id
         ORDER BY p2.payment_created_at DESC
         LIMIT 1),
        'no_payments'
    ) AS detailed_payment_status,
    
    CASE 
        WHEN i.invoice_id IS NOT NULL AND r.receipt_id IS NOT NULL THEN 'invoice_and_receipt'
        WHEN i.invoice_id IS NOT NULL THEN 'invoice'
        WHEN r.receipt_id IS NOT NULL THEN 'receipt'
        ELSE 'no_document'
    END AS document_type,
    
    'direct_order' AS operation_type,
    
    COALESCE(
        (SELECT p2.payment_method
         FROM payment p2
         WHERE p2.payment_invoice_id = i.invoice_id
         AND p2.payment_status IN ('completed', 'partial')
         ORDER BY p2.payment_created_at DESC
         LIMIT 1),
        'not_paid'
    ) AS payment_method,
    
    COALESCE(
        (SELECT p2.payment_reference
         FROM payment p2
         WHERE p2.payment_invoice_id = i.invoice_id
         AND p2.payment_status IN ('completed', 'partial')
         ORDER BY p2.payment_created_at DESC
         LIMIT 1),
        NULL
    ) AS payment_reference,
    
    'order_based' AS source_table,
    
    COALESCE(
        i.invoice_created_at,
        po.placed_order_creation
    ) AS operation_date,
    
    NULL AS cart_status

FROM ordered_item oi
LEFT JOIN placed_order po ON po.id_placed_order = oi.order_ref
LEFT JOIN invoice i ON i.invoice_id = po.placed_order_invoice_ref
LEFT JOIN receipt r ON r.receipt_id = po.placed_order_receipt_ref
WHERE oi.ordered_item_cart_ref IS NULL 
AND oi.order_ref IS NOT NULL
AND oi.ordered_product_id IS NOT NULL

ORDER BY operation_date DESC;

INSERT INTO `gluttex`.`ingredient` (ingredient_name) VALUES 
('Wheat'), 
('Barley'), 
('Rye'), 
('Oats');
INSERT INTO `gluttex`.`ingredient` (ingredient_name) VALUES 
('Corn'), 
('Rice'), 
('Soy'), 
('Milk');
INSERT INTO `gluttex`.`ingredient` (ingredient_name) VALUES 
('Egg'), 
('Peanuts'), 
('Tree Nuts'), 
('Fish');
INSERT INTO `gluttex`.`ingredient` (ingredient_name) VALUES 
('Shellfish'), 
('Lentils'), 
('Chickpeas'), 
('Buckwheat');
INSERT INTO `gluttex`.`ingredient` (ingredient_name) VALUES 
('Almond'), 
('Coconut'), 
('Sunflower Seeds');
INSERT INTO `gluttex`.`ingredient` (ingredient_name) VALUES 
('Pumpkin Seeds'), 
('Sesame Seeds'), 
('Potato'), 
('Sweet Potato');
INSERT INTO `gluttex`.`ingredient` (ingredient_name) VALUES 
('Gelatin'), 
('Lupin'), 
('Mustard');
INSERT INTO `gluttex`.`ingredient` (ingredient_name) VALUES 
('Fennel'), 
('Cumin');
INSERT INTO `gluttex`.`ingredient` (ingredient_name) VALUES 
('Ginger');
INSERT INTO `gluttex`.`ingredient` (ingredient_name) VALUES 
('Garlic');
INSERT INTO `gluttex`.`ingredient` (ingredient_name) VALUES 
('Onion');
INSERT INTO `gluttex`.`ingredient` (ingredient_name) VALUES 
('Leek'), 
('Shallot'), 
('Scallion'), 
('Chive'), 
('Parsley');
INSERT INTO `gluttex`.`ingredient` (ingredient_name) VALUES 
('Cilantro'), 
('Basil'), 
('Oregano'), 
('Thyme');
INSERT INTO `gluttex`.`ingredient` (ingredient_name) VALUES 
('Rosemary'), 
('Sage'), 
('Mint'), 
('Lemongrass');
INSERT INTO `gluttex`.`ingredient` (ingredient_name) VALUES 
('Lavender'), 
('Paprika'), 
('Chili Pepper'), 
('Black Pepper');
INSERT INTO `gluttex`.`ingredient` (ingredient_name) VALUES 
('White Pepper'), 
('Green Pepper'), 
('Red Pepper'), 
('Cinnamon'), 
('Allspice');
INSERT INTO `gluttex`.`ingredient` (ingredient_name) VALUES 
('Butter'), 
('Margarine'), 
('Vegetable Oil'), 
('Baking Powder');
INSERT INTO `gluttex`.`ingredient` (ingredient_name) VALUES 
('Baking Soda'), 
('Cornstarch'), 
('All-Purpose Flour');
INSERT INTO `gluttex`.`ingredient` (ingredient_name) VALUES  
('Pastry Flour'), 
('Self-Rising Flour'); 


update management_rule set management_rule_code = 16383 where id_management_rule >0;

select * from product_provider, provider_details where  idprovider_details_id=product_provider_details_id;

select * from product_provider ;



-- Person Details (base information for individuals)
INSERT INTO person_details (person_first_name, person_last_name, person_birth_date, person_gender, person_country_code, person_phone) VALUES
('Ahmed', 'Benali', '1985-03-15', 'MALE', '213', '+213551234567'),
('Fatima', 'Zohra', '1990-07-22', 'FEMALE', '213', '+213552345678'),
('Mohamed', 'Khelifa', '1978-11-08', 'MALE', '213', '+213553456789'),
('Nadia', 'Bensalem', '1995-01-30', 'FEMALE', '213', '+213554567890'),
('Karim', 'Mansouri', '1982-09-12', 'MALE', '213', '+213555678901'),
('Samira', 'Hadj', '1988-04-25', 'FEMALE', '213', '+213556789012'),
('Yacine', 'Meziane', '1992-12-03', 'MALE', '213', '+213557890123'),
('Leila', 'Boukadoum', '1980-06-18', 'FEMALE', '213', '+213558901234'),
('Rachid', 'Ferhat', '1975-10-10', 'MALE', '213', '+213559012345'),
('Amira', 'Saidi', '1998-08-07', 'FEMALE', '213', '+213560123456'),
('Hakim', 'Bouaziz', '1987-02-28', 'MALE', '213', '+213561234567'),
('Sofia', 'Khemiri', '1993-05-14', 'FEMALE', '213', '+213562345678'),
('Youcef', 'Lounis', '1970-11-20', 'MALE', '213', '+213563456789'),
('Meriem', 'Taleb', '1984-09-03', 'FEMALE', '213', '+213564567890'),
('Ali', 'Boukhelifa', '1991-07-19', 'MALE', '213', '+213565678901'),
('Djamila', 'Ouahab', '1976-12-25', 'FEMALE', '213', '+213566789012'),
('Nassim', 'Cherif', '1983-03-08', 'MALE', '213', '+213567890123'),
('Karima', 'Benaissa', '1989-06-30', 'FEMALE', '213', '+213568901234'),
('Slimane', 'Kaddour', '1972-08-15', 'MALE', '213', '+213569012345'),
('Zahra', 'Moussaoui', '1996-01-12', 'FEMALE', '213', '+213570123456'),
('Abdelkader', 'Benslimane', '1981-10-05', 'MALE', '213', '+213571234567'),
('Noura', 'Dahmani', '1986-04-22', 'FEMALE', '213', '+213572345678'),
('Fares', 'Boutaleb', '1994-11-11', 'MALE', '213', '+213573456789'),
('Hania', 'Zeroual', '1997-02-14', 'FEMALE', '213', '+213574567890'),
('Walid', 'Gherbi', '1979-05-28', 'MALE', '213', '+213575678901');

-- Persons (linking person_details to other entities)
-- Assuming person_details inserted with IDs from 1 to 25
INSERT INTO person (person_details_id, person_blood_type, person_location_id) VALUES
(1, "A+", NULL),   -- Ahmed Benali, A+
(2, "O+", NULL),   -- Fatima Zohra, O+
(3, "B+", NULL),   -- Mohamed Khelifa, B+
(4, "A+", NULL),   -- Nadia Bensalem, A+
(5, "AB+", NULL),   -- Karim Mansouri, AB+
(6, "O+", NULL),   -- Samira Hadj, O+
(7, "A+", NULL),   -- Yacine Meziane, A+
(8, "B+", NULL),   -- Leila Boukadoum, B+
(9, "AB+", NULL),   -- Rachid Ferhat, AB+
(10, "O+", NULL),  -- Amira Saidi, O+
(11, "A+", NULL),  -- Hakim Bouaziz, A+
(12, "B+", NULL),  -- Sofia Khemiri, B+
(13, "O+", NULL),  -- Youcef Lounis, O+
(14, "AB+", NULL),  -- Meriem Taleb, AB+
(15, "A+", NULL),  -- Ali Boukhelifa, A+
(16, "O+", NULL),  -- Djamila Ouahab, O+
(17, "B+", NULL),  -- Nassim Cherif, B+
(18, "A+", NULL),  -- Karima Benaissa, A+
(19, "AB+", NULL),  -- Slimane Kaddour, AB+
(20, "O+", NULL),  -- Zahra Moussaoui, O+
(21, "A+", NULL),  -- Abdelkader Benslimane, A+
(22, "B+", NULL),  -- Noura Dahmani, B+
(23, "O+", NULL),  -- Fares Boutaleb, O+
(24, "AB+", NULL),  -- Hania Zeroual, AB+
(25, "A+", NULL);  -- Walid Gherbi, A+


-- App Users (1-10: Regular Users, 11-15: Managers, 16-20: Admins)
INSERT INTO app_user (
    app_user_name, 
    app_user_password, 
    app_user_person_id, 
    app_user_type, 
    app_user_preferences, 
    app_user_image_url, 
    app_user_email, 
    app_user_wallet_id
) VALUES
-- Regular Users (type_id = 1)
('ahmed.benali', 'hashed_password_1', 1, "admin", '{"theme": "light", "language": "fr"}', 'https://randomuser.me/api/portraits/men/1.jpg', 'ahmed.benali@example.com', NULL),
('fatima.zohra', 'hashed_password_2', 2, "admin", '{"theme": "dark", "language": "ar"}', 'https://randomuser.me/api/portraits/women/1.jpg', 'fatima.zohra@example.com', NULL),
('mohamed.khelifa', 'hashed_password_3', 3, "admin", '{"theme": "light", "language": "en"}', 'https://randomuser.me/api/portraits/men/2.jpg', 'mohamed.khelifa@example.com', NULL),
('nadia.bensalem', 'hashed_password_4', 4, "admin", '{"theme": "dark", "language": "fr"}', 'https://randomuser.me/api/portraits/women/2.jpg', 'nadia.bensalem@example.com', NULL),
('karim.mansouri', 'hashed_password_5', 5, "admin", '{"theme": "light", "language": "ar"}', 'https://randomuser.me/api/portraits/men/3.jpg', 'karim.mansouri@example.com', NULL),
('samira.hadj', 'hashed_password_6', 6, "admin", '{"theme": "dark", "language": "en"}', 'https://randomuser.me/api/portraits/women/3.jpg', 'samira.hadj@example.com', NULL),
('yacine.meziane', 'hashed_password_7', 7, "admin", '{"theme": "light", "language": "fr"}', 'https://randomuser.me/api/portraits/men/4.jpg', 'yacine.meziane@example.com', NULL),
('leila.boukadoum', 'hashed_password_8', 8, "admin", '{"theme": "dark", "language": "ar"}', 'https://randomuser.me/api/portraits/women/4.jpg', 'leila.boukadoum@example.com', NULL),
('rachid.ferhat', 'hashed_password_9', 9, "admin", '{"theme": "light", "language": "en"}', 'https://randomuser.me/api/portraits/men/5.jpg', 'rachid.ferhat@example.com', NULL),
('amira.saidi', 'hashed_password_10', 10, "admin", '{"theme": "dark", "language": "fr"}', 'https://randomuser.me/api/portraits/women/5.jpg', 'amira.saidi@example.com', NULL),

-- Managers (type_id = 2)
('hakim.bouaziz', 'hashed_password_11', 11, "admin", '{"theme": "light", "language": "en", "dashboard": "admin"}', 'https://randomuser.me/api/portraits/men/6.jpg', 'hakim.bouaziz@management.com', NULL),
('sofia.khemiri', 'hashed_password_12', 12, "admin", '{"theme": "dark", "language": "fr", "dashboard": "admin"}', 'https://randomuser.me/api/portraits/women/6.jpg', 'sofia.khemiri@management.com', NULL),
('youcef.lounis', 'hashed_password_13', 13, "admin", '{"theme": "light", "language": "ar", "dashboard": "admin"}', 'https://randomuser.me/api/portraits/men/7.jpg', 'youcef.lounis@management.com', NULL),
('meriem.taleb', 'hashed_password_14', 14, "admin", '{"theme": "dark", "language": "en", "dashboard": "admin"}', 'https://randomuser.me/api/portraits/women/7.jpg', 'meriem.taleb@management.com', NULL),
('ali.boukhelifa', 'hashed_password_15', 15, "admin", '{"theme": "light", "language": "fr", "dashboard": "admin"}', 'https://randomuser.me/api/portraits/men/8.jpg', 'ali.boukhelifa@management.com', NULL),

-- Admins (type_id = 3)
('djamila.ouahab', 'hashed_password_16', 16, "admin", '{"theme": "dark", "language": "ar", "dashboard": "admin", "super_admin": true}', 'https://randomuser.me/api/portraits/women/8.jpg', 'djamila.ouahab@admin.com', NULL),
('nassim.cherif', 'hashed_password_17', 17, "admin", '{"theme": "light", "language": "en", "dashboard": "admin", "super_admin": true}', 'https://randomuser.me/api/portraits/men/9.jpg', 'nassim.cherif@admin.com', NULL),
('karima.benaissa', 'hashed_password_18', 18, "admin", '{"theme": "dark", "language": "fr", "dashboard": "admin", "super_admin": true}', 'https://randomuser.me/api/portraits/women/9.jpg', 'karima.benaissa@admin.com', NULL),
('slimane.kaddour', 'hashed_password_19', 19, "admin", '{"theme": "light", "language": "ar", "dashboard": "admin", "super_admin": true}', 'https://randomuser.me/api/portraits/men/10.jpg', 'slimane.kaddour@admin.com', NULL),
('zahra.moussaoui', 'hashed_password_20', 20, "admin", '{"theme": "dark", "language": "en", "dashboard": "admin", "super_admin": true}', 'https://randomuser.me/api/portraits/women/10.jpg', 'zahra.moussaoui@admin.com', NULL),

-- Additional regular users
('abdelkader.benslimane', 'hashed_password_21', 21, "admin", '{"theme": "light", "language": "fr"}', 'https://randomuser.me/api/portraits/men/11.jpg', 'abdelkader.benslimane@example.com', NULL),
('noura.dahmani', 'hashed_password_22', 22, "admin", '{"theme": "dark", "language": "ar"}', 'https://randomuser.me/api/portraits/women/11.jpg', 'noura.dahmani@example.com', NULL),
('fares.boutaleb', 'hashed_password_23', 23, "admin", '{"theme": "light", "language": "en"}', 'https://randomuser.me/api/portraits/men/12.jpg', 'fares.boutaleb@example.com', NULL),
('hania.zeroual', 'hashed_password_24', 24, "admin", '{"theme": "dark", "language": "fr"}', 'https://randomuser.me/api/portraits/women/12.jpg', 'hania.zeroual@example.com', NULL),
('walid.gherbi', 'hashed_password_25', 25, "admin", '{"theme": "light", "language": "ar"}', 'https://randomuser.me/api/portraits/men/13.jpg', 'walid.gherbi@example.com', NULL);



-- Notifications for user #4 (assuming user exists with id_app_user = 4)

-- Organizations for suppliers
INSERT INTO provider_organisation (
    provider_organisation_name, 
    provider_organisation_desc
) VALUES
('Gluttex International', 'Leading provider of gluten-free products and specialty food items across North Africa. Committed to quality and innovation in celiac-friendly nutrition.'),
('MediFarm Algérie', 'Agricultural cooperative specializing in organic grains, legumes, and traditional Algerian produce. Focus on sustainable farming and fair trade practices.'),
('Sahara Fresh Distribution', 'Major distributor of fresh produce, dairy products, and packaged goods serving retail chains across Algeria. Fast delivery and competitive pricing.'),
('El Djazair Food Industries', 'Food manufacturing company producing traditional Algerian pastries, couscous, and preserved goods. Family-owned since 1985.'),
('Atlas Mountains Organic', 'Specialized in organic and natural food products sourced from the Atlas Mountains region. Focus on honey, dried fruits, and aromatic herbs.');


-- Invitation Notifications for Organizations and Suppliers
INSERT INTO notification (notification_code, notification_params, notification_user_ref, notification_created_at, notification_read_at) VALUES

-- Organization Invitations (referencing the 5 organizations)
('ROLE_INVITATION', '{"entity_id": 1, "entity_name": "Gluttex International", "entity_type": "organization", "role_name": "Store Manager", "invited_by": "Admin User", "invitation_date": "2024-06-01T10:30:00", "management_rule_id": 101}', 4, '2024-06-01 10:30:00', NULL),
('ROLE_INVITATION', '{"entity_id": 2, "entity_name": "MediFarm Algérie", "entity_type": "organization", "role_name": "Product Manager", "invited_by": "Sarah Johnson", "invitation_date": "2024-06-05T14:15:00", "management_rule_id": 102}', 4, '2024-06-05 14:15:00', '2024-06-06 09:20:00'),
('ROLE_INVITATION', '{"entity_id": 3, "entity_name": "Sahara Fresh Distribution", "entity_type": "organization", "role_name": "Inventory Manager", "invited_by": "Michael Brown", "invitation_date": "2024-06-10T09:45:00", "management_rule_id": 103}', 4, '2024-06-10 09:45:00', NULL),
('ROLE_INVITATION', '{"entity_id": 4, "entity_name": "El Djazair Food Industries", "entity_type": "organization", "role_name": "Quality Control Manager", "invited_by": "Ahmed Benali", "invitation_date": "2024-06-12T11:00:00", "management_rule_id": 104}', 4, '2024-06-12 11:00:00', NULL),
('ROLE_INVITATION', '{"entity_id": 5, "entity_name": "Atlas Mountains Organic", "entity_type": "organization", "role_name": "Procurement Specialist", "invited_by": "Fatima Zohra", "invitation_date": "2024-06-15T13:30:00", "management_rule_id": 105}', 4, '2024-06-15 13:30:00', NULL),

-- Supplier Invitations (referencing 7 suppliers)
('ROLE_INVITATION', '{"entity_id": 1, "entity_name": "Gluttex North Algeria", "entity_type": "supplier", "role_name": "Supplier Admin", "invited_by": "Admin User", "invitation_date": "2024-06-02T09:00:00", "management_rule_id": 201}', 4, '2024-06-02 09:00:00', '2024-06-02 10:30:00'),
('ROLE_INVITATION', '{"entity_id": 2, "entity_name": "Gluttex South Region", "entity_type": "supplier", "role_name": "Regional Manager", "invited_by": "Admin User", "invitation_date": "2024-06-03T14:00:00", "management_rule_id": 202}', 4, '2024-06-03 14:00:00', NULL),
('ROLE_INVITATION', '{"entity_id": 3, "entity_name": "MediFarm Central", "entity_type": "supplier", "role_name": "Farm Coordinator", "invited_by": "Sarah Johnson", "invitation_date": "2024-06-07T10:00:00", "management_rule_id": 203}', 4, '2024-06-07 10:00:00', '2024-06-08 08:00:00'),
('ROLE_INVITATION', '{"entity_id": 4, "entity_name": "Sahara Fresh Algiers", "entity_type": "supplier", "role_name": "Logistics Manager", "invited_by": "Michael Brown", "invitation_date": "2024-06-09T15:30:00", "management_rule_id": 204}', 4, '2024-06-09 15:30:00', NULL),
('ROLE_INVITATION', '{"entity_id": 5, "entity_name": "El Djazair Traditional", "entity_type": "supplier", "role_name": "Production Supervisor", "invited_by": "Ahmed Benali", "invitation_date": "2024-06-11T11:00:00", "management_rule_id": 205}', 4, '2024-06-11 11:00:00', '2024-06-12 14:00:00'),
('ROLE_INVITATION', '{"entity_id": 6, "entity_name": "Atlas Honey Products", "entity_type": "supplier", "role_name": "Quality Inspector", "invited_by": "Fatima Zohra", "invitation_date": "2024-06-13T09:00:00", "management_rule_id": 206}', 4, '2024-06-13 09:00:00', NULL),
('ROLE_INVITATION', '{"entity_id": 7, "entity_name": "Sahara Oasis Dates", "entity_type": "supplier", "role_name": "Date Specialist", "invited_by": "Karim Mansouri", "invitation_date": "2024-06-14T14:00:00", "management_rule_id": 207}', 4, '2024-06-14 14:00:00', NULL),

-- System Alert Notifications
('service_reminder', '{"alert_type": "maintenance", "message": "System maintenance scheduled for June 15th at 2 AM", "timestamp": "2024-06-08T16:20:00"}', 4, '2024-06-08 16:20:00', '2024-06-08 17:00:00'),
('service_reminder', '{"alert_type": "security", "message": "New login detected from new device", "timestamp": "2024-06-12T08:15:00"}', 4, '2024-06-12 08:15:00', '2024-06-12 08:30:00'),
('service_reminder', '{"alert_type": "update", "message": "New version 2.0.0 is available", "timestamp": "2024-06-14T11:00:00"}', 4, '2024-06-14 11:00:00', NULL),

-- Reminder Notifications
('event_reminder', '{"reminder_type": "order", "due_date": "2024-06-20", "created_at": "2024-06-13T10:00:00"}', 4, '2024-06-13 10:00:00', NULL),
('event_reminder', '{"reminder_type": "payment", "due_date": "2024-06-25", "created_at": "2024-06-14T09:30:00"}', 4, '2024-06-14 09:30:00', NULL),
('event_reminder', '{"reminder_type": "subscription", "due_date": "2024-07-01", "created_at": "2024-06-15T14:45:00"}', 4, '2024-06-15 14:45:00', '2024-06-16 08:00:00'),

-- Order Status Notifications
('order_shipped', '{"order_id": "ORD-12345", "status": "shipped", "tracking_number": "TRK789012", "updated_at": "2024-06-02T15:30:00"}', 4, '2024-06-02 15:30:00', '2024-06-02 16:00:00'),
('order_delivered', '{"order_id": "ORD-12346", "status": "delivered", "delivered_at": "2024-06-07T12:00:00"}', 4, '2024-06-07 12:00:00', '2024-06-07 13:15:00'),
('order_processing', '{"order_id": "ORD-12347", "status": "processing", "estimated_delivery": "2024-06-22"}', 4, '2024-06-10 11:20:00', NULL),

-- Stock Alert Notifications
('product_stock_low', '{"product_name": "Premium Coffee Beans", "current_stock": 15, "min_threshold": 20, "alert_at": "2024-06-03T08:00:00"}', 4, '2024-06-03 08:00:00', '2024-06-03 09:30:00'),
('product_stock_low', '{"product_name": "Organic Tea", "current_stock": 8, "min_threshold": 10, "alert_at": "2024-06-09T10:15:00"}', 4, '2024-06-09 10:15:00', NULL),
('product_stock_low', '{"product_name": "Gluten-Free Flour", "current_stock": 25, "min_threshold": 30, "alert_at": "2024-06-11T14:30:00"}', 4, '2024-06-11 14:30:00', NULL),

-- Promotional Notifications
('promotional_offer', '{"promo_code": "SUMMER20", "discount": "20%", "expires_at": "2024-07-31", "message": "Summer sale! Get 20% off on all orders"}', 4, '2024-06-01 00:00:00', '2024-06-01 10:00:00'),
('promotional_offer', '{"promo_code": "FREESHIP", "discount": "free shipping", "expires_at": "2024-06-30", "message": "Free shipping on orders over DZD 5000"}', 4, '2024-06-05 09:00:00', NULL),
('promotional_offer', '{"promo_code": "WELCOME10", "discount": "10%", "expires_at": "2024-07-15", "message": "Welcome discount for new customers"}', 4, '2024-06-10 08:00:00', NULL);

-- Summary counts
-- SELECT COUNT(*) FROM notification WHERE notification_user_ref = 4;  -- Should return 18
-- SELECT COUNT(*) FROM notification WHERE notification_user_ref = 4 AND notification_read_at IS NOT NULL;  -- Read count: 6
-- SELECT COUNT(*) FROM notification WHERE notification_user_ref = 4 AND notification_read_at IS NULL;  -- Unread count: 12

-- Management Rules (Role Invitations) for user #4
-- These represent pending invitations for the user to join organizations or suppliers


desc provider_organisation;

select * from notification;
select * from product_provider_type;
desc person_details;
select * from product_provider, provider_details where product_provider.product_provider_details_id = provider_details.idprovider_details_id ;
desc notification;
desc management_rule;
select * from recipe;
select * from notification;
select * from management_rule;
delete from management_rule where id_management_rule = 19;


