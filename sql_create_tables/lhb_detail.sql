CREATE TABLE `s_lhb_detail` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `trade_date` int(10) unsigned NOT NULL,
  `item_code` char(6) NOT NULL DEFAULT '',
  `serial_number` tinyint(1) unsigned NOT NULL DEFAULT '1' COMMENT '买卖前五营业部的序号',
  `sc_name` varchar(32) NOT NULL DEFAULT '' COMMENT '营业部名称',
  `buying` decimal(12,2) unsigned NOT NULL DEFAULT '0.00' COMMENT '营业部买入金额',
  `selling` decimal(12,2) unsigned NOT NULL DEFAULT '0.00' COMMENT '营业部卖出金额',
  `sc_id` varchar(32) NOT NULL DEFAULT '0' COMMENT '营业部ID',
  `direction` varchar(6) NOT NULL DEFAULT 'BUY' COMMENT 'BUY:买入；SELL：卖出',
  `causes` varchar(255) NOT NULL DEFAULT '' COMMENT '上榜原因',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4