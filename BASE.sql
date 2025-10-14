CREATE TABLE "clicks" (
	"id" SERIAL NOT NULL,
	"url" TEXT NULL DEFAULT NULL,
	"timestamp" TIMESTAMP NULL DEFAULT now(),
	"text" TEXT NULL DEFAULT NULL,
	"page_url" TEXT NULL DEFAULT NULL,
	"page_title" TEXT NULL DEFAULT NULL,
	"mechanism" TEXT NULL DEFAULT NULL,
	PRIMARY KEY ("id")
)
;
COMMENT ON COLUMN "clicks"."id" IS '';
COMMENT ON COLUMN "clicks"."url" IS '';
COMMENT ON COLUMN "clicks"."timestamp" IS '';
COMMENT ON COLUMN "clicks"."text" IS '';
COMMENT ON COLUMN "clicks"."page_url" IS '';
COMMENT ON COLUMN "clicks"."page_title" IS '';
COMMENT ON COLUMN "clicks"."mechanism" IS '';
