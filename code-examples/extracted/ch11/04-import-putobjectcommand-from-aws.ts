import { PutObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

const command = new PutObjectCommand({
  Bucket: "my-app-files",
  Key: "users/123/photo.jpg",
  ContentType: "image/jpeg"
});

const url = await getSignedUrl(s3, command, {
  expiresIn: 300
});
