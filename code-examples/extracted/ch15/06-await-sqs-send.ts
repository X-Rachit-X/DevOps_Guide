await sqs.send(
  new SendMessageCommand({
    QueueUrl: process.env.ORDER_QUEUE_URL,
    MessageBody: JSON.stringify({
      orderId,
      userId,
    }),
  })
);
