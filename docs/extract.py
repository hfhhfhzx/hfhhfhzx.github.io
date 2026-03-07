import base64
import struct
import sys

def extract_ed25519_from_ssh(ssh_file, output_priv, output_pub):
    """从 OpenSSH 密钥文件提取 Ed25519 密钥"""
    
    with open(ssh_file, 'r') as f:
        lines = f.readlines()
    
    # 提取 base64 内容
    content = ''
    in_key = False
    for line in lines:
        if 'BEGIN OPENSSH PRIVATE KEY' in line:
            in_key = True
            continue
        if 'END OPENSSH PRIVATE KEY' in line:
            break
        if in_key and line.strip():
            content += line.strip()
    
    if not content:
        print("错误：无法找到密钥内容")
        return False
    
    # Base64 解码
    decoded = base64.b64decode(content)
    
    # OpenSSH 格式解析
    pos = 15  # 跳过 "openssh-key-v1\0"
    
    # 跳过 ciphername
    ciphername_len = struct.unpack('>I', decoded[pos:pos+4])[0]
    pos += 4 + ciphername_len
    
    # 跳过 kdfname
    kdfname_len = struct.unpack('>I', decoded[pos:pos+4])[0]
    pos += 4 + kdfname_len
    
    # 跳过 kdfoptions
    kdfoptions_len = struct.unpack('>I', decoded[pos:pos+4])[0]
    pos += 4 + kdfoptions_len
    
    # 公钥数量
    num_keys = struct.unpack('>I', decoded[pos:pos+4])[0]
    pos += 4
    
    # 提取公钥（最后32字节）
    public_key = None
    for i in range(num_keys):
        pubkey_len = struct.unpack('>I', decoded[pos:pos+4])[0]
        pos += 4
        pubkey = decoded[pos:pos+pubkey_len]
        pos += pubkey_len
        public_key = pubkey[-32:]  # 公钥是最后32字节
    
    # 私钥部分
    priv_len = struct.unpack('>I', decoded[pos:pos+4])[0]
    pos += 4
    private_data = decoded[pos:pos+priv_len]
    
    # 跳过前面的检查值和密钥类型等，找到真正的私钥数据
    priv_pos = 0
    # 跳过 check1, check2 (8字节)
    priv_pos += 8
    # 跳过密钥类型长度和内容
    key_type_len = struct.unpack('>I', private_data[priv_pos:priv_pos+4])[0]
    priv_pos += 4 + key_type_len
    # 跳过公钥
    pubkey_len = struct.unpack('>I', private_data[priv_pos:priv_pos+4])[0]
    priv_pos += 4 + pubkey_len
    # 现在 priv_pos 指向私钥长度
    privkey_len = struct.unpack('>I', private_data[priv_pos:priv_pos+4])[0]
    priv_pos += 4
    # 真正的私钥数据
    privkey_data = private_data[priv_pos:priv_pos+privkey_len]
    
    # Ed25519 私钥是前 32 字节
    private_key = privkey_data[:32]
    
    # 保存私钥
    with open(output_priv, 'wb') as f:
        f.write(private_key)
    print(f"私钥已保存: {output_priv} ({len(private_key)} 字节)")
    # print(f"私钥 HEX: {private_key.hex()}")
    
    # 保存公钥
    if public_key:
        with open(output_pub, 'wb') as f:
            f.write(public_key)
        print(f"公钥已保存: {output_pub} ({len(public_key)} 字节)")
        # print(f"公钥 HEX: {public_key.hex()}")
        return True
    
    return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ssh_key = sys.argv[1]
    else:
        ssh_key = "id_ed25519"
    
    extract_ed25519_from_ssh(ssh_key, "private_key", "public_key")