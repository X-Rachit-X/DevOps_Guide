export const handler = async (event) => {
  for (const record of event.Records) {
    const message = JSON.parse(record.body);

    await processOrder(message.orderId);
  }
};
