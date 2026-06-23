-- ====================================================================
-- POBLADO DE DATOS (SEEDS)
-- ====================================================================

-- 1. Insertar Tiers de Rendimiento
INSERT INTO component_tiers (tier_name, description) VALUES 
('Gama Baja', 'Componentes de entrada, configuraciones de oficina o presupuestos muy ajustados.'),
('Gama Media', 'El est├índar de la industria. Ideal para jugar a 1080p y tareas de desarrollo.'),
('Gama Alta', 'Rendimiento entusiasta, streaming, renderizado y juego a 1440p o 4K.');

-- 2. Insertar Componentes (Catálogo Maestro)
-- 6 categorías × 3 gamas = cobertura completa del catálogo (20 componentes)
INSERT INTO component (name, categoria, component_tiers_id) VALUES 
-- GPUs (3 gamas)
('NVIDIA GeForce GTX 1650',    'GPU', 1),   -- id 1  Gama Baja
('NVIDIA GeForce RTX 3060',    'GPU', 2),   -- id 2  Gama Media
('NVIDIA GeForce RTX 4070',    'GPU', 3),   -- id 3  Gama Alta
('AMD Radeon RX 6600',         'GPU', 2),   -- id 4  Gama Media
-- CPUs (3 gamas)
('Intel Core i3-12100F',       'CPU', 1),   -- id 5  Gama Baja
('Intel Core i5-13400F',       'CPU', 2),   -- id 6  Gama Media
('AMD Ryzen 5 5600X',          'CPU', 2),   -- id 7  Gama Media
('AMD Ryzen 7 7800X3D',        'CPU', 3),   -- id 8  Gama Alta
-- RAM (3 gamas)
('Crucial DDR4 8GB 3200MHz',              'RAM', 1),  -- id 9  Gama Baja
('Kingston Fury Beast DDR4 16GB 3200MHz', 'RAM', 2),  -- id 10 Gama Media
('Corsair Vengeance DDR5 32GB 5600MHz',   'RAM', 3),  -- id 11 Gama Alta
-- Storage (3 gamas)
('SSD Kingston NV2 1TB NVMe',       'Storage', 2),   -- id 12 Gama Media
('SSD Crucial BX500 480GB SATA',    'Storage', 1),   -- id 13 Gama Baja
('SSD Samsung 990 Pro 2TB NVMe',    'Storage', 3),   -- id 17 Gama Alta  (auto_increment, ids 14-16 pre-existentes)
-- PSU (3 gamas)
('Fuente MSI MAG A650BN 650W',      'Power Supply', 2),  -- id 15 Gama Media
('Fuente Cooler Master MWE 500W',   'Power Supply', 1),  -- id 18 Gama Baja
('Fuente Corsair RM1000x 1000W',    'Power Supply', 3),  -- id 19 Gama Alta
-- Case (3 gamas)
('Gabinete MSI Forge 112R',         'Case', 2),  -- id 16 Gama Media
('Gabinete Cougar MX330-X',         'Case', 1),  -- id 20 Gama Baja
('Gabinete Lian Li O11 Dynamic EVO','Case', 3);  -- id 21 Gama Alta

-- 3. Insertar Datos de Steam Hardware Survey (Cruce con nuestros IDs)
INSERT INTO steam_hardware_survey (component_id, global_share_percentage, survey_date) VALUES 
(1,  4.56, '2026-05-01'),  -- GTX 1650
(2,  6.20, '2026-05-01'),  -- RTX 3060
(3,  1.80, '2026-05-01'),  -- RTX 4070
(6,  3.50, '2026-05-01'),  -- i5-13400F
(7,  4.10, '2026-05-01'),  -- Ryzen 5 5600X
(9,  15.30, '2026-05-01'), -- 8GB de RAM
(10, 42.10, '2026-05-01'), -- 16GB de RAM
(11, 28.50, '2026-05-01'), -- 32GB de RAM
(12, 50.03, '2026-05-01'), -- SSD 1TB NVMe
(13, 17.71, '2026-05-01'), -- SSD 480GB SATA
(17, 10.20, '2026-05-01'), -- SSD 2TB NVMe
(15, 55.00, '2026-05-01'); -- PSU 650W (simulado)

-- 4. Insertar Precios de Mercado Externo (API eBay / Amazon)
INSERT INTO market_prices_external (component_id, price_clp) VALUES 
(1,  110000),  -- GTX 1650
(2,  290000),  -- RTX 3060
(3,  560000),  -- RTX 4070
(4,  220000),  -- RX 6600
(5,  85000),   -- i3-12100F
(6,  170000),  -- i5-13400F
(7,  125000),  -- Ryzen 5 5600X
(8,  380000),  -- Ryzen 7 7800X3D
(9,  18000),   -- DDR4 8GB
(10, 35000),   -- DDR4 16GB
(11, 120000),  -- DDR5 32GB
(12, 95000),   -- SSD 1TB NVMe
(13, 30000),   -- SSD 480GB SATA
(17, 185000),  -- SSD Samsung 990 Pro 2TB
(15, 50000),   -- Fuente 650W (Gama Media)
(18, 28000),   -- Fuente 500W (Gama Baja)
(19, 145000),  -- Fuente 1000W (Gama Alta)
(16, 75000),   -- Gabinete MSI Forge 112R
(20, 30000),   -- Gabinete Cougar MX330-X
(21, 180000);  -- Gabinete Lian Li O11 Dynamic EVO

-- 5. Insertar Inventario Real de la Tienda (Simulando los insights del README)
INSERT INTO store_inventory (component_id, stock_qty, store_price_clp) VALUES 
(1,  45, 175000),  -- SOBRESTOCK: demasiadas GTX 1650 a precio alto
(2,  3,  330000),  -- Poco stock de un producto altamente demandado
(3,  2,  670000),  -- PRECIO ALTO: en eBay a 560k, nosotros a 670k
(7,  12, 140000),  -- Ryzen 5 5600X
(10, 0,  450000),  -- ALERTA DE STOCK: Kingston 16GB en 0
(14, 5,  220000),  -- SSD Samsung 990 Pro 2TB
(16, 20, 32000),   -- Fuente 500W (stock alto, gama baja)
(19, 15, 35000),   -- Gabinete Cougar MX330-X
(20, 2,  210000);  -- Gabinete Lian Li O11 Dynamic EVO

-- 6. Insertar Historial de Ventas de la Tienda
INSERT INTO store_sales (quantity_sold, sale_date, component_id) VALUES 
(1, '2026-06-10', 1),
(2, '2026-06-12', 2),
(1, '2026-06-15', 3),
(5, '2026-06-18', 12),
(3, '2026-06-20', 7);

-- 7. Insertar Cat├ílogo de Videojuegos (Kaggle)
INSERT INTO games (titulo, release_year) VALUES 
  ('Cyberpunk 2077', 2020),
  ('Counter-Strike: Global Offensive', 2012),
  ('Valorant', 2020),
  ('Elden Ring', 2022),
  ('Grand Theft Auto V', 2015),
  ('Fortnite', 2017),
  ('Hogwarts Legacy', 2023),
  ('Red Dead Redemption 2', 2018),
  ('Minecraft', 2011),
  ('League of Legends', 2009),
  ('Call of Duty: Warzone', 2020),
  ('The Witcher 3: Wild Hunt', 2015),
  ('Apex Legends', 2019),
  ('Overwatch 2', 2022),
  ('Baldur''s Gate 3', 2023);

-- 8. Insertar Requisitos de Hardware por Juego
INSERT INTO game_requeriments (games_id, component_id, requirement_type) VALUES 
  -- 1. Cyberpunk 2077
  (1, 6, 'Minimum'), (1, 1, 'Minimum'), (1, 9, 'Minimum'), (1, 13, 'Minimum'), (1, 14, 'Minimum'),
  (1, 7, 'Recommended'), (1, 2, 'Recommended'), (1, 10, 'Recommended'), (1, 12, 'Recommended'), (1, 14, 'Recommended'),
  
  -- 2. CS:GO
  (2, 5, 'Minimum'), (2, 1, 'Minimum'), (2, 9, 'Minimum'), (2, 13, 'Minimum'), (2, 14, 'Minimum'),
  (2, 7, 'Recommended'), (2, 4, 'Recommended'), (2, 10, 'Recommended'), (2, 13, 'Recommended'), (2, 14, 'Recommended'),
  
  -- 3. Valorant
  (3, 5, 'Minimum'), (3, 1, 'Minimum'), (3, 9, 'Minimum'), (3, 13, 'Minimum'), (3, 14, 'Minimum'),
  (3, 6, 'Recommended'), (3, 4, 'Recommended'), (3, 10, 'Recommended'), (3, 13, 'Recommended'), (3, 14, 'Recommended'),
  
  -- 4. Elden Ring
  (4, 7, 'Minimum'), (4, 2, 'Minimum'), (4, 10, 'Minimum'), (4, 12, 'Minimum'), (4, 14, 'Minimum'),
  (4, 8, 'Recommended'), (4, 3, 'Recommended'), (4, 11, 'Recommended'), (4, 12, 'Recommended'), (4, 14, 'Recommended'),

  -- 5. GTA V
  (5, 5, 'Minimum'), (5, 1, 'Minimum'), (5, 9, 'Minimum'), (5, 13, 'Minimum'), (5, 14, 'Minimum'),
  (5, 6, 'Recommended'), (5, 2, 'Recommended'), (5, 10, 'Recommended'), (5, 12, 'Recommended'), (5, 14, 'Recommended'),

  -- 6. Fortnite
  (6, 5, 'Minimum'), (6, 1, 'Minimum'), (6, 9, 'Minimum'), (6, 13, 'Minimum'), (6, 14, 'Minimum'),
  (6, 6, 'Recommended'), (6, 2, 'Recommended'), (6, 10, 'Recommended'), (6, 12, 'Recommended'), (6, 14, 'Recommended'),

  -- 7. Hogwarts Legacy
  (7, 7, 'Minimum'), (7, 2, 'Minimum'), (7, 10, 'Minimum'), (7, 12, 'Minimum'), (7, 14, 'Minimum'),
  (7, 8, 'Recommended'), (7, 3, 'Recommended'), (7, 11, 'Recommended'), (7, 12, 'Recommended'), (7, 14, 'Recommended'),

  -- 8. Red Dead Redemption 2
  (8, 6, 'Minimum'), (8, 1, 'Minimum'), (8, 9, 'Minimum'), (8, 12, 'Minimum'), (8, 14, 'Minimum'),
  (8, 7, 'Recommended'), (8, 2, 'Recommended'), (8, 10, 'Recommended'), (8, 12, 'Recommended'), (8, 14, 'Recommended'),

  -- 9. Minecraft
  (9, 5, 'Minimum'), (9, 1, 'Minimum'), (9, 9, 'Minimum'), (9, 13, 'Minimum'), (9, 14, 'Minimum'),
  (9, 6, 'Recommended'), (9, 4, 'Recommended'), (9, 10, 'Recommended'), (9, 13, 'Recommended'), (9, 14, 'Recommended'),

  -- 10. League of Legends
  (10, 5, 'Minimum'), (10, 1, 'Minimum'), (10, 9, 'Minimum'), (10, 13, 'Minimum'), (10, 14, 'Minimum'),
  (10, 5, 'Recommended'), (10, 1, 'Recommended'), (10, 10, 'Recommended'), (10, 13, 'Recommended'), (10, 14, 'Recommended'),

  -- 11. Call of Duty: Warzone
  (11, 7, 'Minimum'), (11, 2, 'Minimum'), (11, 10, 'Minimum'), (11, 12, 'Minimum'), (11, 14, 'Minimum'),
  (11, 8, 'Recommended'), (11, 3, 'Recommended'), (11, 11, 'Recommended'), (11, 12, 'Recommended'), (11, 14, 'Recommended'),

  -- 12. The Witcher 3: Wild Hunt
  (12, 6, 'Minimum'), (12, 1, 'Minimum'), (12, 9, 'Minimum'), (12, 13, 'Minimum'), (12, 14, 'Minimum'),
  (12, 7, 'Recommended'), (12, 2, 'Recommended'), (12, 10, 'Recommended'), (12, 12, 'Recommended'), (12, 14, 'Recommended'),

  -- 13. Apex Legends
  (13, 6, 'Minimum'), (13, 1, 'Minimum'), (13, 9, 'Minimum'), (13, 13, 'Minimum'), (13, 14, 'Minimum'),
  (13, 7, 'Recommended'), (13, 2, 'Recommended'), (13, 10, 'Recommended'), (13, 12, 'Recommended'), (13, 14, 'Recommended'),

  -- 14. Overwatch 2
  (14, 5, 'Minimum'), (14, 1, 'Minimum'), (14, 9, 'Minimum'), (14, 13, 'Minimum'), (14, 14, 'Minimum'),
  (14, 6, 'Recommended'), (14, 4, 'Recommended'), (14, 10, 'Recommended'), (14, 13, 'Recommended'), (14, 14, 'Recommended'),

  -- 15. Baldur's Gate 3
  (15, 7, 'Minimum'), (15, 2, 'Minimum'), (15, 10, 'Minimum'), (15, 12, 'Minimum'), (15, 14, 'Minimum'),
  (15, 8, 'Recommended'), (15, 3, 'Recommended'), (15, 11, 'Recommended'), (15, 12, 'Recommended'), (15, 14, 'Recommended');

-- 9. Insertar Consultas Simuladas de Usuarios
INSERT INTO user_queries (budget_clp, games_id) VALUES 
(500000, 3),   -- Presupuesto bajo para jugar Valorant
(800000, 1),   -- Presupuesto medio para Cyberpunk
(1200000, 1),  -- Presupuesto alto para Cyberpunk
(650000, 2),   -- Presupuesto para CS2
(1500000, 4);  -- Presupuesto entusiasta para Elden Ring

-- 10. Insertar Plantillas de PC Armados (Build Templates)
INSERT INTO build_templates (template_name, description) VALUES 
('PC Gamer Entrada Economico', 'Configuraci├│n balanceada ideal para estudiantes y juegos competitivos livianos.'),
('PC Gamer Ultra 1080p', 'Dise├▒ado para romper cualquier juego actual en calidad Ultra a m├ís de 60 FPS.'),
('PC Streamer Enthusiast 4K', 'Estaci├│n de trabajo pesada y juegos AAA en m├íxima resoluci├│n.');

-- 11. Relacionar Componentes con las Plantillas (Muchos a Muchos)
INSERT INTO build_components (build_templates_id, component_id) VALUES 
-- Build Economica (Gama Baja)
(1, 1),  -- GTX 1650
(1, 5),  -- i3-12100F
(1, 9),  -- 8GB RAM
(1, 13), -- SSD 480GB SATA
(1, 18), -- Fuente 500W (Gama Baja)
(1, 20), -- Gabinete Cougar MX330-X
-- Build Ultra 1080p (Gama Media)
(2, 2),  -- RTX 3060
(2, 7),  -- Ryzen 5 5600X
(2, 10), -- 16GB RAM
(2, 12), -- SSD 1TB NVMe
(2, 15), -- Fuente 650W (Gama Media)
(2, 16), -- Gabinete MSI Forge 112R
-- Build 4K Enthusiast (Gama Alta)
(3, 3),  -- RTX 4070
(3, 8),  -- Ryzen 7 7800X3D
(3, 11), -- 32GB DDR5
(3, 17), -- SSD Samsung 990 Pro 2TB
(3, 19), -- Fuente Corsair RM1000x 1000W
(3, 21); -- Gabinete Lian Li O11 Dynamic EVO
