/*
SQLyog Ultimate v12.09 (64 bit)
MySQL - 5.7.26 : Database - stock
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`stock` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;

USE `stock`;

/*Table structure for table `s_changes` */

DROP TABLE IF EXISTS `s_changes`;

CREATE TABLE `s_changes` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `trade_date` int(10) unsigned NOT NULL COMMENT '日期',
  `item_code` char(6) CHARACTER SET utf8 NOT NULL COMMENT '代码',
  PRIMARY KEY (`id`),
  KEY `item_code` (`item_code`),
  KEY `trade_date` (`trade_date`)
) ENGINE=InnoDB AUTO_INCREMENT=3279736 DEFAULT CHARSET=utf8mb4 COMMENT='盘中异动';

/*Table structure for table `s_continue_last` */

DROP TABLE IF EXISTS `s_continue_last`;

CREATE TABLE `s_continue_last` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `item_code` varchar(6) CHARACTER SET utf8 NOT NULL DEFAULT '',
  `date_time` int(8) unsigned NOT NULL COMMENT '截止时间',
  `continue_num` smallint(5) unsigned NOT NULL DEFAULT '1' COMMENT '连续天数',
  PRIMARY KEY (`id`),
  UNIQUE KEY `day_num_code` (`date_time`,`continue_num`,`item_code`)
) ENGINE=InnoDB AUTO_INCREMENT=58431 DEFAULT CHARSET=utf8mb4;

/*Table structure for table `s_items` */

DROP TABLE IF EXISTS `s_items`;

CREATE TABLE `s_items` (
  `item_code` varchar(32) NOT NULL,
  `item_name` varchar(32) NOT NULL,
  `item_type` tinyint(1) unsigned NOT NULL DEFAULT '1' COMMENT '1:沪 2：深',
  `item_status` tinyint(1) unsigned NOT NULL DEFAULT '1' COMMENT '状态 1：正常 0：停牌',
  `item_category` tinyint(1) unsigned NOT NULL DEFAULT '1' COMMENT '1:A,2:创业板,3:新三板',
  `item_pe` decimal(16,2) NOT NULL DEFAULT '0.00' COMMENT '市盈率',
  `item_value` bigint(20) unsigned NOT NULL COMMENT '市值',
  `circulate` bigint(20) unsigned NOT NULL COMMENT '流通市值',
  `last_price` decimal(10,2) unsigned NOT NULL COMMENT '最近收盘价',
  `item_time` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '上市时间',
  `issue_num` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT '发行总数',
  `online_issue_num` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT '网上发行数量',
  `issue_price` decimal(6,2) unsigned NOT NULL DEFAULT '1.00' COMMENT '发行价格',
  `peissuea` decimal(10,2) unsigned DEFAULT '0.00' COMMENT '发行市盈率',
  `issue_documents` varchar(32) CHARACTER SET utf8 NOT NULL DEFAULT '' COMMENT '招股书地址，https://pdf.dfcfw.com/pdf/H2_AN202003081375995370_1.pdf',
  `item_url` varchar(255) CHARACTER SET utf8 NOT NULL DEFAULT '' COMMENT '东财公司简介地址',
  `item_industry` varchar(32) CHARACTER SET utf8 NOT NULL DEFAULT '' COMMENT '所属行业',
  `main_business` varchar(255) CHARACTER SET utf8 NOT NULL DEFAULT '' COMMENT '主营业务',
  PRIMARY KEY (`item_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/*Table structure for table `s_open` */

DROP TABLE IF EXISTS `s_open`;

CREATE TABLE `s_open` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `trade_date` int(10) unsigned NOT NULL,
  `item_code` varchar(6) CHARACTER SET utf8 NOT NULL,
  `item_name` varchar(32) CHARACTER SET utf8 NOT NULL,
  `open_f2` decimal(10,2) unsigned NOT NULL DEFAULT '0.00',
  `open_percent_f3` decimal(10,2) DEFAULT '0.00',
  `open_f4` decimal(10,2) DEFAULT NULL,
  `open_volume_f5` int(10) unsigned NOT NULL,
  `open_amount_f6` bigint(20) unsigned NOT NULL,
  `open_f7` decimal(10,2) NOT NULL DEFAULT '0.00',
  `open_turnoverrate_f8` decimal(5,2) unsigned NOT NULL DEFAULT '0.00',
  `open_pe_f9` decimal(10,2) NOT NULL DEFAULT '0.00',
  `open_vol_percent_f10` decimal(5,2) unsigned NOT NULL DEFAULT '1.00',
  `open_type_f13` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `yesterday_close_f18` decimal(10,2) unsigned NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `trade_date` (`trade_date`,`item_code`)
) ENGINE=InnoDB AUTO_INCREMENT=1690747 DEFAULT CHARSET=utf8mb4;

/*Table structure for table `s_strategies` */

DROP TABLE IF EXISTS `s_strategies`;

CREATE TABLE `s_strategies` (
  `strategy_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `proud_name` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '策略名称',
  `marking` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '策略文件名称',
  `account_id` int(10) unsigned NOT NULL,
  `created_at` datetime NOT NULL COMMENT '创建时间',
  `init_assets` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT '该策略的初始化金额',
  `available_assets` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT '该策略剩余的可用金额',
  `assets` bigint(20) NOT NULL DEFAULT '0' COMMENT '最新金额，包含股票市值',
  `deal_number` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '交易次数，买入卖出只算一次',
  `success_number` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '成功次数',
  `success_rate` smallint(6) NOT NULL DEFAULT '0' COMMENT '最新成功率',
  `status` tinyint(1) unsigned NOT NULL DEFAULT '0' COMMENT '0:未启动；1：进行中；2：暂停；3：策略失效',
  `desc` text COLLATE utf8mb4_unicode_ci COMMENT '说明',
  PRIMARY KEY (`strategy_id`),
  UNIQUE KEY `marking` (`marking`),
  KEY `account_id` (`account_id`)
) ENGINE=InnoDB AUTO_INCREMENT=100000002 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

/*Table structure for table `s_strategies_items` */

DROP TABLE IF EXISTS `s_strategies_items`;

CREATE TABLE `s_strategies_items` (
  `strategies_items_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `strategy_id` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '策略ID',
  `trade_date` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '交易日期，在该天需要进行交易',
  `get_date` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '选股日期',
  `item_code` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `yeah` tinyint(1) unsigned NOT NULL DEFAULT '0' COMMENT '1：是它是它就是它',
  `status` tinyint(1) unsigned NOT NULL DEFAULT '0' COMMENT '0：未提交操作；1：已提交；2：仓位不够',
  `notes` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '简要说明',
  `target_price` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '目标价格，如果是0表示实时价格买入',
  `amount` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '买入数量，约定：如果为0表示剩余资金全仓买入',
  PRIMARY KEY (`strategies_items_id`),
  KEY `trade_date` (`trade_date`),
  KEY `strategy_id` (`strategy_id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='策略项目表';

/*Table structure for table `s_trade_account` */

DROP TABLE IF EXISTS `s_trade_account`;

CREATE TABLE `s_trade_account` (
  `trade_account_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `account_id` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '账户ID',
  `trade_date` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '日期',
  `total_assets` bigint(20) NOT NULL DEFAULT '0' COMMENT '总资金',
  `available_assets` bigint(20) NOT NULL DEFAULT '0' COMMENT '可用金额',
  `stock_assets` bigint(20) NOT NULL DEFAULT '0' COMMENT '股票市值',
  `frozen_assets` bigint(20) NOT NULL DEFAULT '0' COMMENT '冻结金额',
  `updated_at` datetime NOT NULL COMMENT '更新时间',
  PRIMARY KEY (`trade_account_id`),
  KEY `trade_date` (`trade_date`),
  KEY `account_id` (`account_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='账户每日变化表';

/*Table structure for table `s_trade_day_kline` */

DROP TABLE IF EXISTS `s_trade_day_kline`;

CREATE TABLE `s_trade_day_kline` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `item_code` char(6) CHARACTER SET utf8 NOT NULL,
  `trade_date` int(8) unsigned NOT NULL DEFAULT '10000000' COMMENT '成交日期20180909',
  `volume` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT '成交数量',
  `yclose` decimal(7,2) unsigned NOT NULL DEFAULT '0.00' COMMENT '上一日的收盘价',
  `open` decimal(7,2) unsigned NOT NULL DEFAULT '0.00' COMMENT '开盘价',
  `high` decimal(7,2) unsigned NOT NULL DEFAULT '0.00' COMMENT '最高价',
  `low` decimal(7,2) unsigned NOT NULL DEFAULT '0.00' COMMENT '最低价',
  `close` decimal(7,2) unsigned NOT NULL DEFAULT '0.00' COMMENT '收盘价',
  `chg` decimal(7,2) NOT NULL DEFAULT '0.00' COMMENT '涨跌额',
  `stock_rise` decimal(7,2) unsigned NOT NULL DEFAULT '0.00' COMMENT '涨停价',
  `stock_fall` decimal(7,2) unsigned NOT NULL DEFAULT '0.00' COMMENT '跌停价',
  `is_last` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否涨停或跌停1涨停2跌停0',
  `percent` decimal(6,2) NOT NULL DEFAULT '0.00' COMMENT '涨跌百分比',
  `amplitude` decimal(6,2) unsigned NOT NULL DEFAULT '0.00' COMMENT '振幅',
  `turnoverrate` decimal(6,2) unsigned NOT NULL DEFAULT '0.00' COMMENT '换手率',
  `psy` decimal(12,5) NOT NULL DEFAULT '0.00000',
  `psyma` decimal(12,5) NOT NULL DEFAULT '0.00000',
  `pe` decimal(12,5) NOT NULL DEFAULT '0.00000',
  `pb` decimal(12,5) NOT NULL DEFAULT '0.00000',
  `ps` decimal(12,5) NOT NULL DEFAULT '0.00000',
  `pcf` decimal(12,5) NOT NULL DEFAULT '0.00000',
  `market_capital` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT '总市值',
  `circulate` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT '流通市值',
  `vol_percent` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '前一日量比(100%)',
  `amount` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT '成交额',
  `morning_low_price` decimal(10,2) unsigned NOT NULL DEFAULT '0.00' COMMENT '早盘9:30至11:30的最低价',
  `day_percent_close` decimal(10,2) unsigned NOT NULL DEFAULT '0.00' COMMENT '日均价格',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code_trade_date` (`item_code`,`trade_date`),
  KEY `trade_date` (`trade_date`)
) ENGINE=InnoDB AUTO_INCREMENT=7571989 DEFAULT CHARSET=utf8mb4;

/*Table structure for table `s_trade_list` */

DROP TABLE IF EXISTS `s_trade_list`;

CREATE TABLE `s_trade_list` (
  `trade_list_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `account_id` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '账户ID',
  `trade_date` int(11) NOT NULL DEFAULT '0' COMMENT '日期',
  `direction` enum('BUY','SELL') COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'BUY:买入；SELL：卖出，注意：买入状态在前，先买入再卖出，是不是没有毛病？',
  `item_code` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `assets` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '买入/卖出价格',
  `amount` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '数量',
  `strategy_id` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '策略',
  `cost_assets` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT '成本价格，包含了手续费印花税等',
  `deal_amount` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '成交数量',
  `status` tinyint(1) unsigned NOT NULL DEFAULT '0' COMMENT '0:未成交;1:全部成交;2:部分成交;',
  `stop_loss` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '止损价',
  PRIMARY KEY (`trade_list_id`),
  KEY `trade_date` (`trade_date`),
  KEY `account_id` (`account_id`),
  KEY `strategy_id` (`strategy_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
