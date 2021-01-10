CREATE TABLE `s_concepts` (
  `id` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `item_code` char(6) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `item_name` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `concept_list` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '板块列表',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci