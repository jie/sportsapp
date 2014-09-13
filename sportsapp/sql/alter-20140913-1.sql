ALTER TABLE `sportsapp`.`user` ADD COLUMN `avatar` varchar(128) DEFAULT NULL  AFTER `email` ;
ALTER TABLE `sportsapp`.`user` ADD COLUMN `status` tinyint(4) DEFAULT '0'  AFTER `update_at` ;