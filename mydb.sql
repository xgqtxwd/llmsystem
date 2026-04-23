/*
 Navicat Premium Dump SQL

 Source Server         : setting
 Source Server Type    : MySQL
 Source Server Version : 50743 (5.7.43-log)
 Source Host           : 8.137.169.98:3306
 Source Schema         : mydb

 Target Server Type    : MySQL
 Target Server Version : 50743 (5.7.43-log)
 File Encoding         : 65001

 Date: 16/03/2026 22:03:01
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for chat_records
-- ----------------------------
DROP TABLE IF EXISTS `chat_records`;
CREATE TABLE `chat_records`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `user_id` bigint(20) NULL DEFAULT NULL COMMENT '用户ID',
  `question` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '用户问题',
  `answer` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT 'AI回答',
  `created_at` datetime NULL DEFAULT NULL COMMENT '对话时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `user_id`(`user_id`) USING BTREE,
  CONSTRAINT `chat_records_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = 'AI对话记录表，用于保存用户与营养顾问AI的对话' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for diet_record_items
-- ----------------------------
DROP TABLE IF EXISTS `diet_record_items`;
CREATE TABLE `diet_record_items`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `record_id` bigint(20) NULL DEFAULT NULL COMMENT '饮食记录ID',
  `food_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '食物名称',
  `quantity` float NULL DEFAULT NULL COMMENT '食用数量',
  `calories` float NULL DEFAULT NULL COMMENT '摄入热量',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `record_id`(`record_id`) USING BTREE,
  CONSTRAINT `diet_record_items_ibfk_1` FOREIGN KEY (`record_id`) REFERENCES `diet_records` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '饮食明细表，用于记录每次饮食的具体食物' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for diet_records
-- ----------------------------
DROP TABLE IF EXISTS `diet_records`;
CREATE TABLE `diet_records`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `user_id` bigint(20) NULL DEFAULT NULL COMMENT '用户ID',
  `meal_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '餐次类型',
  `record_time` datetime NULL DEFAULT NULL COMMENT '记录时间',
  `total_calories` float NULL DEFAULT NULL COMMENT '总热量',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `user_id`(`user_id`) USING BTREE,
  CONSTRAINT `diet_records_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '用户饮食记录表，用于记录用户每天的饮食情况' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for food_recognition_records
-- ----------------------------
DROP TABLE IF EXISTS `food_recognition_records`;
CREATE TABLE `food_recognition_records`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `user_id` bigint(20) NULL DEFAULT NULL COMMENT '用户ID',
  `image_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '图片地址',
  `recognized_food` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '识别食物',
  `confidence` float NULL DEFAULT NULL COMMENT '识别置信度',
  `recognized_at` datetime NULL DEFAULT NULL COMMENT '识别时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `user_id`(`user_id`) USING BTREE,
  CONSTRAINT `food_recognition_records_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '食物识别记录表，用于存储用户上传图片识别结果' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ingredient_nutrition
-- ----------------------------
DROP TABLE IF EXISTS `ingredient_nutrition`;
CREATE TABLE `ingredient_nutrition`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `ingredient_id` bigint(20) NULL DEFAULT NULL COMMENT '食材ID',
  `calories` float NULL DEFAULT NULL COMMENT '热量',
  `protein` float NULL DEFAULT NULL COMMENT '蛋白质',
  `fat` float NULL DEFAULT NULL COMMENT '脂肪',
  `carbohydrate` float NULL DEFAULT NULL COMMENT '碳水化合物',
  `fiber` float NULL DEFAULT NULL COMMENT '膳食纤维',
  `vitamins` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '维生素信息',
  `minerals` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '矿物质信息',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ingredient_id`(`ingredient_id`) USING BTREE,
  CONSTRAINT `ingredient_nutrition_ibfk_1` FOREIGN KEY (`ingredient_id`) REFERENCES `ingredients` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '食材营养成分表，用于记录食材的营养数据' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ingredients
-- ----------------------------
DROP TABLE IF EXISTS `ingredients`;
CREATE TABLE `ingredients`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '食材ID',
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '食材名称',
  `category` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '食材类别',
  `season` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '适宜季节',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '食材描述',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '食材信息表，用于存储系统中的食材基础数据' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for knowledge_embeddings
-- ----------------------------
DROP TABLE IF EXISTS `knowledge_embeddings`;
CREATE TABLE `knowledge_embeddings`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `knowledge_id` bigint(20) NULL DEFAULT NULL COMMENT '知识ID',
  `embedding_vector` blob NULL COMMENT '向量数据',
  `model_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT 'Embedding模型',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `knowledge_id`(`knowledge_id`) USING BTREE,
  CONSTRAINT `knowledge_embeddings_ibfk_1` FOREIGN KEY (`knowledge_id`) REFERENCES `nutrition_knowledge` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '知识向量表，用于RAG检索的向量数据' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for nutrition_knowledge
-- ----------------------------
DROP TABLE IF EXISTS `nutrition_knowledge`;
CREATE TABLE `nutrition_knowledge`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '知识ID',
  `title` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '知识标题',
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '知识内容',
  `category` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '知识分类',
  `source` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '数据来源',
  `created_at` datetime NULL DEFAULT NULL COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '营养知识库表，用于存储系统中的营养科普知识' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for recipe_ingredients
-- ----------------------------
DROP TABLE IF EXISTS `recipe_ingredients`;
CREATE TABLE `recipe_ingredients`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `recipe_id` bigint(20) NULL DEFAULT NULL COMMENT '食谱ID',
  `ingredient_id` bigint(20) NULL DEFAULT NULL COMMENT '食材ID',
  `quantity` float NULL DEFAULT NULL COMMENT '食材用量',
  `unit` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '单位',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `recipe_id`(`recipe_id`) USING BTREE,
  INDEX `ingredient_id`(`ingredient_id`) USING BTREE,
  CONSTRAINT `recipe_ingredients_ibfk_1` FOREIGN KEY (`recipe_id`) REFERENCES `recipes` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `recipe_ingredients_ibfk_2` FOREIGN KEY (`ingredient_id`) REFERENCES `ingredients` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '食谱与食材关联表，用于记录制作食谱所需食材' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for recipe_nutrition
-- ----------------------------
DROP TABLE IF EXISTS `recipe_nutrition`;
CREATE TABLE `recipe_nutrition`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `recipe_id` bigint(20) NULL DEFAULT NULL COMMENT '食谱ID',
  `calories` float NULL DEFAULT NULL COMMENT '热量',
  `protein` float NULL DEFAULT NULL COMMENT '蛋白质',
  `fat` float NULL DEFAULT NULL COMMENT '脂肪',
  `carbohydrate` float NULL DEFAULT NULL COMMENT '碳水化合物',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `recipe_id`(`recipe_id`) USING BTREE,
  CONSTRAINT `recipe_nutrition_ibfk_1` FOREIGN KEY (`recipe_id`) REFERENCES `recipes` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '食谱营养信息表，用于记录每个食谱的营养成分' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for recipes
-- ----------------------------
DROP TABLE IF EXISTS `recipes`;
CREATE TABLE `recipes`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '食谱ID',
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '食谱名称',
  `meal_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '餐次类型',
  `difficulty` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '制作难度',
  `cook_time` int(11) NULL DEFAULT NULL COMMENT '烹饪时间(分钟)',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '食谱介绍',
  `created_at` datetime NULL DEFAULT NULL COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '食谱信息表，用于存储系统中的菜谱数据' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for user_diet_preferences
-- ----------------------------
DROP TABLE IF EXISTS `user_diet_preferences`;
CREATE TABLE `user_diet_preferences`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `user_id` bigint(20) NULL DEFAULT NULL COMMENT '用户ID',
  `taste_preference` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '口味偏好',
  `diet_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '饮食类型',
  `allergies` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '过敏食物',
  `forbidden_foods` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '禁忌食物',
  `updated_at` datetime NULL DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `user_id`(`user_id`) USING BTREE,
  CONSTRAINT `user_diet_preferences_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '用户饮食偏好表，用于记录用户饮食习惯和禁忌' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for user_health_goals
-- ----------------------------
DROP TABLE IF EXISTS `user_health_goals`;
CREATE TABLE `user_health_goals`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `user_id` bigint(20) NULL DEFAULT NULL COMMENT '用户ID',
  `goal_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '目标类型(减肥/增肌/控糖)',
  `target_weight` float NULL DEFAULT NULL COMMENT '目标体重',
  `daily_calorie_target` float NULL DEFAULT NULL COMMENT '每日目标热量',
  `created_at` datetime NULL DEFAULT NULL COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `user_id`(`user_id`) USING BTREE,
  CONSTRAINT `user_health_goals_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '用户健康目标表，用于记录用户设定的健康管理目标' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for user_health_profile
-- ----------------------------
DROP TABLE IF EXISTS `user_health_profile`;
CREATE TABLE `user_health_profile`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `user_id` bigint(20) NULL DEFAULT NULL COMMENT '用户ID',
  `age` int(11) NULL DEFAULT NULL COMMENT '年龄',
  `gender` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '性别',
  `height` float NULL DEFAULT NULL COMMENT '身高(cm)',
  `weight` float NULL DEFAULT NULL COMMENT '体重(kg)',
  `activity_level` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '活动水平',
  `health_conditions` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '健康状况',
  `bmi` float NULL DEFAULT NULL COMMENT '身体质量指数',
  `created_at` datetime NULL DEFAULT NULL COMMENT '记录创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `user_id`(`user_id`) USING BTREE,
  CONSTRAINT `user_health_profile_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '用户健康档案表，用于存储用户的身体健康数据' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '用户唯一ID',
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '用户名',
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '用户邮箱',
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '用户手机号',
  `password_hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '加密后的密码',
  `avatar` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '用户头像URL',
  `created_at` datetime NULL DEFAULT NULL COMMENT '账户创建时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '用户基本信息表，用于存储系统注册用户的基本账户信息' ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
