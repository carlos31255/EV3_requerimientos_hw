-- ====================================================================
-- POBLADO DE DATOS (SEEDS)
-- ====================================================================

-- 1. Insertar Tiers de Rendimiento
INSERT INTO component_tiers (tier_name, description) VALUES 
('Gama Baja', 'Componentes de entrada, configuraciones de oficina o presupuestos muy ajustados.'),
('Gama Media', 'El est├índar de la industria. Ideal para jugar a 1080p y tareas de desarrollo.'),
('Gama Alta', 'Rendimiento entusiasta, streaming, renderizado y juego a 1440p o 4K.');

-- 2. Insertar Componentes (Cat├ílogo Maestro)
INSERT INTO component (name, categoria, component_tiers_id) VALUES 
('NVIDIA GeForce GTX 1650', 'GPU', 1),
('NVIDIA GeForce RTX 3060', 'GPU', 2),
('NVIDIA GeForce RTX 4070', 'GPU', 3),
('AMD Radeon RX 6600', 'GPU', 2),
('Intel Core i3-12100F', 'CPU', 1),
('Intel Core i5-13400F', 'CPU', 2),
('AMD Ryzen 5 5600X', 'CPU', 2),
('AMD Ryzen 7 7800X3D', 'CPU', 3),
('Crucial DDR4 8GB 3200MHz', 'RAM', 1),
('Kingston Fury Beast DDR4 16GB 3200MHz', 'RAM', 2),
('Corsair Vengeance DDR5 32GB 5600MHz', 'RAM', 3),
('SSD Kingston NV2 1TB NVMe', 'Storage', 2),
('SSD Crucial BX500 480GB SATA', 'Storage', 1),
('Fuente MSI MAG A650BN 650W', 'Power Supply', 2),
('Gabinete MSI Forge 112R', 'Case', 2);

-- 3. Insertar Datos de Steam Hardware Survey (Cruce con nuestros IDs)
INSERT INTO steam_hardware_survey (component_id, global_share_percentage, survey_date) VALUES 
(1, 4.56, '2026-05-01'), -- GTX 1650
(2, 6.20, '2026-05-01'), -- RTX 3060
(3, 1.80, '2026-05-01'), -- RTX 4070
(6, 3.50, '2026-05-01'), -- i5-13400F
(7, 4.10, '2026-05-01'), -- Ryzen 5 5600X
(9, 15.30, '2026-05-01'), -- 8GB de RAM
(10, 42.10, '2026-05-01'), -- 16GB de RAM en general
(11, 28.50, '2026-05-01'); -- 32GB de RAM

-- 4. Insertar Precios de Mercado Externo (API eBay / Amazon)
INSERT INTO market_prices_external (component_id, price_clp) VALUES 
(1, 110000),  -- GTX 1650
(2, 290000),  -- RTX 3060
(3, 560000),  -- RTX 4070
(4, 220000),  -- RX 6600
(5, 85000),   -- i3-12100F
(6, 170000),  -- i5-13400F
(7, 125000),  -- Ryzen 5 5600X
(8, 380000),  -- Ryzen 7 7800X3D
(9, 18000),   -- DDR4 8GB
(10, 35000),  -- DDR4 16GB
(11, 120000), -- DDR5 32GB
(12, 95000),  -- SSD 1TB
(13, 30000),  -- SSD 480GB
(14, 50000);  -- Fuente 650W

-- 5. Insertar Inventario Real de la Tienda (Simulando los insights del README)
INSERT INTO store_inventory (component_id, stock_qty, store_price_clp) VALUES 
(1, 45, 175000),  -- CASO SOBRESTOCK: Tenemos demasiadas 1650 y caras
(2, 3, 330000),   -- Poco stock de un producto altamente demandado
(3, 2, 670000),   -- CASO PRECIO ALTO: En eBay est├í a 560k, nosotros a 670k (Poco competitivos)
(7, 12, 140000),
(10, 0, 450000);  -- ALERTA DE STOCK: Kingston 16GB en stock 0

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
('Counter-Strike 2', 2023),
('Valorant', 2020),
('Elden Ring', 2022),
('GTA V', 2015);

-- 8. Insertar Requisitos de Hardware por Juego
INSERT INTO game_requeriments (games_id, component_id, requirement_type) VALUES 
-- Cyberpunk Minimum: i5, GTX 1650, 8GB RAM, SSD 480, Fuente 650W, Gabinete
(1, 6, 'Minimum'),
(1, 1, 'Minimum'),
(1, 9, 'Minimum'),
(1, 13, 'Minimum'),
(1, 14, 'Minimum'),

-- Cyberpunk Recommended: Ryzen 5, RTX 3060, 16GB RAM, SSD 1TB, Fuente 650W, Gabinete
(1, 7, 'Recommended'),
(1, 2, 'Recommended'),
(1, 10, 'Recommended'),
(1, 12, 'Recommended'),
(1, 14, 'Recommended'),

-- CS2 Minimum
(2, 5, 'Minimum'),
(2, 1, 'Minimum'),
(2, 9, 'Minimum'),
-- Valorant Minimum
(3, 5, 'Minimum'),
(3, 1, 'Minimum'),
(3, 9, 'Minimum'),
-- Elden Ring Recommended
(4, 8, 'Recommended'),
(4, 3, 'Recommended'),
(4, 11, 'Recommended');

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
(1, 1),  -- Build Econ├│mica usa la GTX 1650
(1, 5),  -- Usa el i3
(1, 9),  -- Usa 8GB de RAM
(2, 2),  -- Build Ultra usa la RTX 3060
(2, 7),  -- Usa el Ryzen 5 5600X
(2, 10), -- Usa 16GB de RAM
(3, 3),  -- Build 4K usa la RTX 4070
(3, 8),  -- Usa el Ryzen 7 7800X3D
(3, 11); -- Usa 32GB de DDR5
