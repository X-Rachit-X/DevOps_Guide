import {
  PutObjectCommand
} from "@aws-sdk/client-s3";

await s3.send(
  new PutObjectCommand({
    Bucket: "my-app-files",
    Key: "users/123/profile.jpg",
    Body: fileBuffer,
    ContentType: "image/jpeg"
  })
);
