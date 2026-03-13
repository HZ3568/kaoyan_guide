DROP TABLE IF EXISTS `university_new`;

CREATE TABLE `university_new` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `avatar` VARCHAR(255) DEFAULT NULL,
  `province_id` INT DEFAULT NULL,
  `address` VARCHAR(255) DEFAULT NULL,
  `school_type` VARCHAR(50) DEFAULT NULL,
  `education_level` VARCHAR(50) DEFAULT NULL,
  `is_985` TINYINT(1) NOT NULL DEFAULT 0,
  `is_211` TINYINT(1) NOT NULL DEFAULT 0,
  `is_double_first_class` TINYINT(1) NOT NULL DEFAULT 0,
  `official_website` VARCHAR(255) DEFAULT NULL,
  `description` LONGTEXT,
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `university_new` (
  `id`, `name`, `avatar`, `province_id`, `address`,
  `school_type`, `education_level`, `is_985`, `is_211`, `is_double_first_class`,
  `official_website`, `description`
)
SELECT
  `id`,
  IFNULL(`name`, CONCAT('院校-', `id`)),
  `avatar`,
  `areas_id`,
  `address`,
  `characters`,
  `level`,
  IF(`level` = '985' OR `level` LIKE '%985%', 1, 0),
  IF(`level` = '211' OR `level` LIKE '%211%', 1, 0),
  IF(`characters` LIKE '%双一流%', 1, 0),
  `official_website`,
  `content`
FROM `university`;

RENAME TABLE `university` TO `university_legacy_backup`, `university_new` TO `university`;
