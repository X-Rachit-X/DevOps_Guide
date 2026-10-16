import { Pool } from "pg";
import Redis from "ioredis";
import { SQSClient } from "@aws-sdk/client-sqs";

const required = (name: string): string => {
  const v = process.env[name];
  if (!v) throw new Error(`Missing required env var ${name}`);
  return v;
};

export const config = {
  port: Number(process.env.PORT ?? 3000),
  databaseUrl: required("DATABASE_URL"),
  redisUrl: process.env.REDIS_URL,
  queueUrl: required("SQS_QUEUE_URL"),
  region: process.env.AWS_REGION ?? "ap-south-1",
  endpoint: process.env.AWS_ENDPOINT_URL, // set only for LocalStack
};

// Size the pool so that replicas * max <= DB max_connections (Chapters 13 and 35 section 39).
export const pool = new Pool({ connectionString: config.databaseUrl, max: Number(process.env.DB_POOL_MAX ?? 10) });
export const redis = config.redisUrl ? new Redis(config.redisUrl, { lazyConnect: true, maxRetriesPerRequest: 1 }) : null;
export const sqs = new SQSClient({ region: config.region, endpoint: config.endpoint });
