#### ZN，LSPIT，TS 安装包里面的 machikado 是什么？如何生成？

当我们查看 ZygiskNext, LSPosed IT, TrickyStore 的安装包时，我们会发现有几个格格不入的存在，它们就是 machikado，格式是 machikado.架构

## 它们是什么？

当我们下载 [ZygiskNext 最后公开的源码](https://github.com/Dr-TSNG/ZygiskNext/archive/refs/tags/v4-0.9.1.1.zip)，打开 module/build.gradle.kts，会发现里面有这样的代码

```kotlin
            if (file("private_key").exists()) {
                println("=== machikado intergity signing ===")
                val privateKey = file("private_key").readBytes()
                val publicKey = file("public_key").readBytes()
                val namedSpec = NamedParameterSpec("ed25519")
                val privKeySpec = EdECPrivateKeySpec(namedSpec, privateKey)
                val kf = KeyFactory.getInstance("ed25519")
                val privKey = kf.generatePrivate(privKeySpec);
                val sig = Signature.getInstance("ed25519")
                fun File.sha(realFile: File? = null) {
                    val path = this.path.replace("\\", "/")
                    sig.update(this.name.toByteArray())
                    sig.update(0) // null-terminated string
                    val real = realFile ?: this
                    val buffer = ByteBuffer.allocate(8)
                        .order(ByteOrder.LITTLE_ENDIAN)
                        .putLong(real.length())
                        .array()
                    sig.update(buffer)
                    real.forEachBlock { bytes, size ->
                        sig.update(bytes, 0, size)
                    }
                }
                //然后定义了一个文件列表
                    sig.initSign(privKey)
                    set.forEach { it.first.sha(it.second) }
                    val signFile = root.file(name).asFile
                    signFile.writeBytes(sig.sign())
                    signFile.appendBytes(publicKey)
                }

                getSign("machikado.arm", "armeabi-v7a", "arm64-v8a")
                getSign("machikado.x86", "x86", "x86_64")
            } else {
                println("no private_key found, this build will not be signed")
                root.file("machikado.arm").asFile.createNewFile()
                root.file("machikado.x86").asFile.createNewFile()
            }
```

这说明，machikado 是一个包含 Ed25519 签名（它会把所有列表中的文件组合在一起再计算 sha256，然后用私钥签名，生成一个64字节的签名）和 公钥（32字节）的文件（96字节）

为什么 machikado 会分架构呢？因为模块的 binary 和 library 有架构之分。因为不同的架构有不同的代码，导致它们的哈希不同，这样导致 machikado 必须也要按架构调整，否则会验证失败（模块在安装时不会提取所有架构的 binary 和 library）

为什么 machikado 在这里不分 32位 和 64位呢？因为这个版本的 ZN 它会同时提取 32位 和 64位 的 binary 和 library

## 如何生成

**WIP**
