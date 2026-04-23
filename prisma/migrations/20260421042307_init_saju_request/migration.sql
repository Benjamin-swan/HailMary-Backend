-- CreateTable
CREATE TABLE `saju_request` (
    `id` VARCHAR(40) NOT NULL,
    `birth` DATE NOT NULL,
    `birthTime` VARCHAR(5) NULL,
    `calendar` VARCHAR(8) NOT NULL,
    `gender` VARCHAR(8) NOT NULL,
    `birthCity` VARCHAR(32) NOT NULL,
    `sajuData` JSON NOT NULL,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),

    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
