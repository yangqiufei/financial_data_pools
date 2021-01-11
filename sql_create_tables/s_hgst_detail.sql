CREATE TABLE `s_hgst_detail` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `trade_date` int(10) unsigned NOT NULL COMMENT '日期：HdDate',
  `item_code` varchar(6) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `item_name` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `industry_name` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '所属行业名称：HYName',
  `industry_code` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '所属行业代码：HYCode',
  `institutions_sum` smallint(5) unsigned NOT NULL DEFAULT '0' COMMENT '机构总数:JG_SUM',
  `shares_rate` double NOT NULL DEFAULT '0' COMMENT '占总股本比例:SharesRate',
  `share_hold` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT '持股数量:ShareHold',
  `share_capital` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT '持股市值:ShareSZ',
  `equity_rate` double NOT NULL DEFAULT '0' COMMENT '占流通股比例:LTZB',
  `total_equity_rate` double NOT NULL DEFAULT '0' COMMENT '占总股本比例:ZZB',
  `share_hold_chg` bigint(20) NOT NULL DEFAULT '0' COMMENT '当日持股数量变化:ShareHold_Chg_One',
  `share_capital_chg` bigint(20) NOT NULL DEFAULT '0' COMMENT '当日持股市值变化:ShareSZ_Chg_One',
  `share_capital_chg_rate` double NOT NULL DEFAULT '0' COMMENT '当日持股市值变化比例:ShareSZ_Chg_Rate_One',
  `circulate_chg_rate` double NOT NULL DEFAULT '0' COMMENT '当日流通市值变化比例:LTZB_One',
  `capital_chg_rate` double NOT NULL DEFAULT '0' COMMENT '当日总市值变化比例:ZZB_One',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci

