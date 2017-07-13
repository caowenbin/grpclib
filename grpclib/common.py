import struct


async def recv_gen(stream, message_type):
    while True:
        meta = await stream.recv_data(5)
        if not meta:
            break

        compressed_flag = struct.unpack('?', meta[:1])[0]
        if compressed_flag:
            raise NotImplementedError('Compression not implemented')

        message_len = struct.unpack('>I', meta[1:])[0]
        message_bin = await stream.recv_data(message_len)
        assert len(message_bin) == message_len, \
            '{} != {}'.format(len(message_bin), message_len)
        message = message_type.FromString(message_bin)
        yield message


async def send(stream, message, end_stream=False):
    reply_bin = message.SerializeToString()
    reply_data = (struct.pack('?', False)
                  + struct.pack('>I', len(reply_bin))
                  + reply_bin)
    await stream.send_data(reply_data, end_stream=end_stream)
