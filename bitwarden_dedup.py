import json

# Your RAM disk file paths here
VAULT_WITH_DUPS_PATH = "/mnt/ramdisk/my_bitwarden_export.json"
VAULT_DEDUPED_OUTPUT_PATH = "/mnt/ramdisk/my_unencrypted_deduped_bitwarden_export.json"

def dedup(vault_with_dups_path, vault_deduped_output_path, paranoid=True):
    with open(vault_with_dups_path, encoding='utf-8', mode='r') as vaultfile:
        vault_json = json.load(vaultfile)

    assert not vault_json["encrypted"], """Unfortunately you need to export your vault unencrypted.
    BitWarden seems to use a login item's unique id as salt (or something like that), so there would
    be no duplicates in the encrypted file."""

    items = vault_json["items"]

    # use a set to detect duplicates.
    # two json item objects are duplicates if and only if, after their "id" keys are removed, they 
    # have the same string representations (same value of json.dumps).
    item_identities = set()

    # will be the new contents of the "items" map
    deduped_items = []

    for item in items:
        item_id = item["id"]
        # delete id since it's the one thing that's different in otherwise-exact duplicate items
        # rather than `del` it, just set it to "", since otherwise it moves the key in the ordered dict, which results
        # in a different ordering in the json output.
        item["id"] = ""
        item_identity = json.dumps(item)
        if item_identity not in item_identities:
            item_identities.add(item_identity)
            # add the id back 
            item["id"] = item_id
            deduped_items.append(item)

    vault_json["items"] = deduped_items

    print(f"{len(items) - len(item_identities)} duplicates removed.")
    print(f"Exported file has {len(item_identities)} login/password/secret items.")

    with open(vault_deduped_output_path, encoding='utf-8', mode='w') as newvaultfile:
        # need ensure_ascii=False because bitwarden doesn't escape unicode characters 
        json.dump(vault_json, newvaultfile, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    dedup(VAULT_WITH_DUPS_PATH, VAULT_DEDUPED_OUTPUT_PATH)

