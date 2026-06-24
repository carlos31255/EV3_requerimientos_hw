-- ====================================================================
-- POBLADO DE DATOS (SEEDS) — IDs FORZADOS PARA CONSISTENCIA
-- ====================================================================

-- 1. Tiers de Rendimiento
INSERT INTO component_tiers (id, tier_name, description) VALUES 
(1, 'Gama Baja',  'Componentes de entrada, configuraciones de oficina o presupuestos muy ajustados.'),
(2, 'Gama Media', 'El estándar de la industria. Ideal para jugar a 1080p y tareas de desarrollo.'),
(3, 'Gama Alta',  'Rendimiento entusiasta, streaming, renderizado y juego a 1440p o 4K.');

-- 2. Catálogo Maestro de Componentes (6 categorías × 3 gamas = 20 componentes)
INSERT INTO component (id, name, categoria, component_tiers_id) VALUES 
-- GPUs
(1,  'NVIDIA GeForce GTX 1650',             'GPU',          1),
(2,  'NVIDIA GeForce RTX 3060',             'GPU',          2),
(3,  'NVIDIA GeForce RTX 4070',             'GPU',          3),
(4,  'AMD Radeon RX 6600',                  'GPU',          2),
-- CPUs
(5,  'Intel Core i3-12100F',                'CPU',          1),
(6,  'Intel Core i5-13400F',                'CPU',          2),
(7,  'AMD Ryzen 5 5600X',                   'CPU',          2),
(8,  'AMD Ryzen 7 7800X3D',                 'CPU',          3),
-- RAM
(9,  'Crucial DDR4 8GB 3200MHz',            'RAM',          1),
(10, 'Kingston Fury Beast DDR4 16GB 3200MHz','RAM',         2),
-- Storage
(12, 'SSD Kingston NV2 1TB NVMe',           'Storage',      2),
(13, 'SSD Crucial BX500 480GB SATA',        'Storage',      1),
(14, 'SSD Samsung 990 Pro 2TB NVMe',        'Storage',      3),
-- Power Supply
(15, 'Fuente MSI MAG A650BN 650W',          'Power Supply', 2),
(16, 'Fuente Cooler Master MWE 500W',       'Power Supply', 1),
(17, 'Fuente Corsair RM1000x 1000W',        'Power Supply', 3);

-- 3. Steam Hardware Survey
INSERT INTO steam_hardware_survey (component_id, global_share_percentage, survey_date) VALUES 
(1, 2.56, '2026-05-01'),
(2, 6.20, '2026-05-01'),
(3, 1.80, '2026-05-01'),
(4, 0.95, '2026-05-01'),
(5, 1.20, '2026-05-01'),
(6, 3.50, '2026-05-01'),
(7, 4.10, '2026-05-01'),
(8, 0.85, '2026-05-01'),
(9, 15.30, '2026-05-01'),
(10, 42.10, '2026-05-01'),
(13, 17.71, '2026-05-01'),
(12, 50.03, '2026-05-01'),
(14, 10.20, '2026-05-01');

-- 4. Precios de Mercado Externo (eBay API)
INSERT INTO market_prices_external (component_id, price_clp) VALUES 
(1,  110000),
(2,  290000),
(3,  560000),
(4,  220000),
(5,  85000),
(6,  170000),
(7,  125000),
(8,  380000),
(9,  18000),
(10, 35000),
(12, 95000),
(13, 30000),
(14, 185000),
(15, 50000),
(16, 28000),
(17, 145000);   -- Gabinete Lian Li O11 Dynamic EVO

-- 5. Inventario
INSERT INTO store_inventory (component_id, stock_qty, store_price_clp) VALUES 
(1,  45, 175000),
(2,  3,  330000),
(3,  2,  670000),
(4,  10, 260000),
(5,  25, 105000),
(6,  8,  205000),
(7,  12, 140000),
(8,  4,  420000),
(9,  50, 25000),
(10, 0,  450000),
(12, 30, 115000),
(13, 15, 45000),
(14, 5,  220000),
(15, 8,  65000),
(16, 20, 32000),
(17, 5,  160000);   -- Gabinete Lian Li

-- 6. Historial de Ventas
INSERT INTO store_sales (component_id, quantity_sold, sale_date) VALUES 
(1, 5, '2026-06-01'),
(2, 12, '2026-06-02'),
(3, 1, '2026-06-03'),
(7, 8, '2026-06-04'),
(10, 20, '2026-06-06'),
(12, 15, '2026-06-07'),
(15, 4, '2026-06-08'),
(13, 6, '2026-06-09'),
(8, 2, '2026-06-10'),
(17, 1, '2026-06-11');

-- 7. Catálogo de Videojuegos (Kaggle)
INSERT INTO games (id, titulo, release_year) VALUES 
(1,  'Cyberpunk 2077',                  2020),
(2,  'Counter-Strike: Global Offensive', 2012),
(3,  'Valorant',                         2020),
(4,  'Elden Ring',                       2022),
(5,  'Grand Theft Auto V',               2015),
(6,  'Fortnite',                         2017),
(7,  'Hogwarts Legacy',                  2023),
(8,  'Red Dead Redemption 2',            2018),
(9,  'Minecraft',                        2011),
(10, 'League of Legends',                2009),
(11, 'Call of Duty: Warzone',            2020),
(12, 'The Witcher 3: Wild Hunt',         2015),
(13, 'Apex Legends',                     2019),
(14, 'Overwatch 2',                      2022),
(15, 'Baldur''s Gate 3',                 2023);

-- 8. Requisitos de Hardware por Juego
INSERT INTO game_requeriments (games_id, component_id, requirement_type) VALUES 
-- 1. Cyberpunk 2077
(1, 6,  'Minimum'),     -- i5-13400F
(1, 1,  'Minimum'),     -- GTX 1650
(1, 9,  'Minimum'),     -- 8GB RAM
(1, 13, 'Minimum'),     -- SSD 480GB
(1, 15, 'Minimum'),     -- Fuente 650W
(1, 7,  'Recommended'), -- Ryzen 5 5600X
(1, 2,  'Recommended'), -- RTX 3060
(1, 10, 'Recommended'), -- 16GB RAM
(1, 12, 'Recommended'), -- SSD 1TB
(1, 15, 'Recommended'), -- Fuente 650W

-- 2. CS:GO / Counter-Strike
(2, 5,  'Minimum'),
(2, 1,  'Minimum'),
(2, 9,  'Minimum'),
(2, 13, 'Minimum'),
(2, 15, 'Minimum'),
(2, 7,  'Recommended'),
(2, 4,  'Recommended'),
(2, 9,  'Recommended'),
(2, 13, 'Recommended'),
(2, 15, 'Recommended'),

-- 3. Valorant
(3, 5,  'Minimum'),
(3, 1,  'Minimum'),
(3, 9,  'Minimum'),
(3, 13, 'Minimum'),
(3, 15, 'Minimum'),
(3, 6,  'Recommended'),
(3, 4,  'Recommended'),
(3, 9,  'Recommended'),
(3, 13, 'Recommended'),
(3, 15, 'Recommended'),

-- 4. Elden Ring
(4, 7,  'Minimum'),
(4, 2,  'Minimum'),
(4, 10, 'Minimum'),
(4, 12, 'Minimum'),
(4, 15, 'Minimum'),
(4, 8,  'Recommended'),
(4, 3,  'Recommended'),
(4, 10, 'Recommended'),
(4, 12, 'Recommended'),
(4, 17, 'Recommended'),

-- 5. GTA V
(5, 5,  'Minimum'),
(5, 1,  'Minimum'),
(5, 9,  'Minimum'),
(5, 13, 'Minimum'),
(5, 15, 'Minimum'),
(5, 6,  'Recommended'),
(5, 2,  'Recommended'),
(5, 10, 'Recommended'),
(5, 12, 'Recommended'),
(5, 15, 'Recommended'),

-- 6. Fortnite
(6, 5,  'Minimum'),
(6, 1,  'Minimum'),
(6, 9,  'Minimum'),
(6, 13, 'Minimum'),
(6, 15, 'Minimum'),
(6, 6,  'Recommended'),
(6, 2,  'Recommended'),
(6, 10, 'Recommended'),
(6, 12, 'Recommended'),
(6, 15, 'Recommended'),

-- 7. Hogwarts Legacy
(7, 7,  'Minimum'),
(7, 2,  'Minimum'),
(7, 10, 'Minimum'),
(7, 12, 'Minimum'),
(7, 15, 'Minimum'),
(7, 8,  'Recommended'),
(7, 3,  'Recommended'),
(7, 10, 'Recommended'),
(7, 12, 'Recommended'),
(7, 17, 'Recommended'),

-- 8. Red Dead Redemption 2
(8, 6,  'Minimum'),
(8, 1,  'Minimum'),
(8, 9,  'Minimum'),
(8, 12, 'Minimum'),
(8, 15, 'Minimum'),
(8, 7,  'Recommended'),
(8, 2,  'Recommended'),
(8, 9,  'Recommended'),
(8, 12, 'Recommended'),
(8, 15, 'Recommended'),

-- 9. Minecraft
(9, 5,  'Minimum'),
(9, 1,  'Minimum'),
(9, 9,  'Minimum'),
(9, 13, 'Minimum'),
(9, 15, 'Minimum'),
(9, 6,  'Recommended'),
(9, 4,  'Recommended'),
(9, 10, 'Recommended'),
(9, 13, 'Recommended'),
(9, 15, 'Recommended'),

-- 10. League of Legends
(10, 5,  'Minimum'),
(10, 1,  'Minimum'),
(10, 9,  'Minimum'),
(10, 13, 'Minimum'),
(10, 15, 'Minimum'),
(10, 5,  'Recommended'),
(10, 1,  'Recommended'),
(10, 10, 'Recommended'),
(10, 13, 'Recommended'),
(10, 15, 'Recommended'),

-- 11. Call of Duty: Warzone
(11, 7,  'Minimum'),
(11, 2,  'Minimum'),
(11, 10, 'Minimum'),
(11, 12, 'Minimum'),
(11, 15, 'Minimum'),
(11, 8,  'Recommended'),
(11, 3,  'Recommended'),
(11, 10, 'Recommended'),
(11, 12, 'Recommended'),
(11, 17, 'Recommended'),

-- 12. The Witcher 3
(12, 6,  'Minimum'),
(12, 1,  'Minimum'),
(12, 9,  'Minimum'),
(12, 13, 'Minimum'),
(12, 15, 'Minimum'),
(12, 7,  'Recommended'),
(12, 2,  'Recommended'),
(12, 10, 'Recommended'),
(12, 12, 'Recommended'),
(12, 15, 'Recommended'),

-- 13. Apex Legends
(13, 6,  'Minimum'),
(13, 1,  'Minimum'),
(13, 9,  'Minimum'),
(13, 13, 'Minimum'),
(13, 15, 'Minimum'),
(13, 7,  'Recommended'),
(13, 2,  'Recommended'),
(13, 10, 'Recommended'),
(13, 12, 'Recommended'),
(13, 15, 'Recommended'),

-- 14. Overwatch 2
(14, 5,  'Minimum'),
(14, 1,  'Minimum'),
(14, 9,  'Minimum'),
(14, 13, 'Minimum'),
(14, 15, 'Minimum'),
(14, 6,  'Recommended'),
(14, 4,  'Recommended'),
(14, 10, 'Recommended'),
(14, 13, 'Recommended'),
(14, 15, 'Recommended'),

-- 15. Baldur's Gate 3
(15, 7,  'Minimum'),
(15, 2,  'Minimum'),
(15, 10, 'Minimum'),
(15, 12, 'Minimum'),
(15, 15, 'Minimum'),
(15, 8,  'Recommended'),
(15, 3,  'Recommended'),
(15, 10, 'Recommended'),
(15, 12, 'Recommended'),
(15, 17, 'Recommended');

-- 9. Consultas Simuladas de Usuarios
INSERT INTO user_queries (budget_clp, games_id) VALUES 
(500000,  3),   -- Valorant presupuesto bajo
(800000,  1),   -- Cyberpunk presupuesto medio
(1200000, 1),   -- Cyberpunk presupuesto alto
(650000,  2),   -- CS2
(1500000, 4);   -- Elden Ring entusiasta

-- 10. Build Templates
INSERT INTO build_templates (id, template_name, description) VALUES 
(1, 'PC Gamer Entrada Economico', 'Configuración balanceada ideal para estudiantes y juegos competitivos livianos.'),
(2, 'PC Gamer Ultra 1080p',       'Diseñado para correr cualquier juego actual en calidad Ultra a más de 60 FPS.'),
(3, 'PC Streamer Enthusiast 4K',  'Estación de trabajo pesada y juegos AAA en máxima resolución.');

-- 11. Build Components (Muchos a Muchos)
INSERT INTO build_components (build_templates_id, component_id) VALUES 
(1, 1),
(1, 5),
(1, 9),
(1, 13),
(1, 16),
(2, 2),
(2, 7),
(2, 10),
(2, 12),
(2, 15),
(3, 3),
(3, 8),
(3, 10),
(3, 14),
(3, 17);  -- Gabinete Lian Li O11 Dynamic EVO
