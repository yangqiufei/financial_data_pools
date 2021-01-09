CREATE TABLE `s_notices` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `notice_date` bigint(20) unsigned NOT NULL,
  `item_code` char(6) COLLATE utf8mb4_unicode_ci DEFAULT '',
  `item_name` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `column_code` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `column_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `art_code` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `title` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `notice_date` (`notice_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci