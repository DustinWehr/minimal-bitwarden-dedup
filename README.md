This is a minimal script to remove exact duplicates from a BitWarden vault, intended to be easy to review.
Approximately 20 source lines of Python with no dependencies except the JSON standard library.

# Usage

## 1. Save other work and close programs

Because you'll restart your computer at the end.

## 2. Make and mount a RAM disk

Don't save your unencrypted vault to persistent storage (HDD/SSD), as you'd need to securely erase 
it, which is not as easy as some might expect.

### Linux (and OSX?)

Makes a 10MB RAM disk.
```
$ sudo mkdir /mnt/ramdisk
$ sudo mount --types tmpfs --options rw,size=10M tmpfs /mnt/ramdisk
```

### Windows

If you know an easy way (without external software?), please tell me, or better yet open a pull request with your tested instructions.


## 3. Review `bitwarden_dedup.py`

Check that I'm not stealing all your passwords.

## 4. Export vault in JSON

Save it to your mounted RAM disk.

Google how to do this for your BitWarden client.

## 5. Dedupe

Replace the path values `VAULT_WITH_DUPS_PATH` and `VAULT_DEDUPED_OUTPUT_PATH` in `bitwarden_dedup.py` 
with the appropriate ones for your RAM disk and exported vault, then do:

```
$ python3 bitwarden_dedup.py
```

Which writes to the file at `VAULT_DEDUPED_OUTPUT_PATH`.

## 6. Purge your BitWarden vault, then import deduped JSON

Google how to do this for your BitWarden client.

## 7. Power cycle your computer

We could overwrite your secrets on the RAM disk, but I can't do anything foolproof in python about the temporary memory that the script uses, which also contained your unencrypted secrets, so turn off and then on your computer now to clear your RAM.

# Test

```
$ python3 run_tests.py
```
