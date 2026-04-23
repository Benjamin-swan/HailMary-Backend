-- CreateTable
CREATE TABLE `saju_survey` (
    `id` VARCHAR(40) NOT NULL,
    `sajuRequestId` VARCHAR(40) NOT NULL,
    `surveyVersion` VARCHAR(16) NOT NULL,
    `step1` JSON NOT NULL,
    `step2` JSON NOT NULL,
    `step3` TEXT NULL,
    `paid` BOOLEAN NOT NULL DEFAULT false,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    UNIQUE INDEX `saju_survey_sajuRequestId_key`(`sajuRequestId`),
    INDEX `saju_survey_paid_createdAt_idx`(`paid`, `createdAt`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- AddForeignKey
ALTER TABLE `saju_survey` ADD CONSTRAINT `saju_survey_sajuRequestId_fkey` FOREIGN KEY (`sajuRequestId`) REFERENCES `saju_request`(`id`) ON DELETE CASCADE ON UPDATE CASCADE;
