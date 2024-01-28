import json
from urllib.parse import urlparse

# Your RAM disk file paths here
VAULT_WITH_DUPS_PATH = "/mnt/ramdisk/my_bitwarden_export.json"
VAULT_DEDUPED_OUTPUT_PATH = "/mnt/ramdisk/my_unencrypted_deduped_bitwarden_export.json"

if not VAULT_WITH_DUPS_PATH or not VAULT_DEDUPED_OUTPUT_PATH:
    print("Please export the VAULT_WITH_DUPS_PATH and VAULT_DEDUPED_OUTPUT_PATH environment variables.")
    sys.exit(1)

class BitwardenItem:
    def __init__(self, item):
        self.content = item
        self.id = item["id"]
        self.content["id"] = ""
        self._key = None

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __hash__(self) -> int:
        if not self._key:
            self._key = hash(self.getKey())
            # print(self.getKey(), self._key)
        return self._key

    def getKey(self) -> str:
        item = self.content
        # "https://github.com" and "https://github.com/login" are different items, but we want to treat them as the same
        name = item.get('name') or '<no name>'

        if 'identity' in item.keys():
            # is identity items
            return name + str(item.get('identity'))
        elif 'card' in item.keys():
            # is card items
            return name + str(item.get('card'))
        elif 'secureNote' in item.keys():
            # is note items
            notes = item["notes"] or ''
            return name + str(notes)
        elif 'login' in item.keys():
            # is login items
                uris: list = item["login"]["uris"]

                if not uris:
                    print(item["name"], "has no uris", item)
                    return name + str(item.get('login'))

                uri = uris[0]["uri"]
                username = item["login"]["username"] or ''

                # https://stackoverflow.com/questions/9626535/get-protocol-host-name-from-url
                parsed_uri = urlparse(uri)
                base_uri = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

                # item["login"]["uris"][0]["uri"] = base_uri
                # return name + str(item.get('login'))
                return name + base_uri + username
        else:
            # print("Error, unhandled type", item)
            return name + str(item)


def dedup(vault_with_dups_path, vault_deduped_output_path):
    with open(vault_with_dups_path, encoding='utf-8', mode='r') as vaultfile:
        vault_json = json.load(vaultfile)

    assert not vault_json["encrypted"], """Unfortunately you need to export your vault unencrypted.
    BitWarden seems to use a login item's unique id as salt (or something like that), so there would
    be no duplicates in the encrypted file."""

    items: list[BitwardenItem] = [BitwardenItem(x) for x in vault_json["items"]]

    # use a set to detect duplicates.
    # two json item objects are duplicates if and only if, after their "id" keys are removed, they
    # have the same string representations (same value of json.dumps).
    item_identities: set[BitwardenItem] = set()

    # will be the new contents of the "items" map
    deduped_items = []

    for item in items:
        # item_id = item.id
        # delete id since it's the one thing that's different in otherwise-exact duplicate items
        # rather than `del` it, just set it to "", since otherwise it moves the key in the ordered dict, which results
        # in a different ordering in the json output.
        # item.id = ""
        item_identity = item
        if item_identity not in item_identities:
            item_identities.add(item_identity)
            # add the id back
            item.content['id'] = item.id
            deduped_items.append(item.content)

    vault_json["items"] = deduped_items

    print(f"{len(items) - len(item_identities)} duplicates removed.")
    print(f"Exported file has {len(item_identities)} login/password/secret items.")

    with open(vault_deduped_output_path, encoding='utf-8', mode='w') as newvaultfile:
        # need ensure_ascii=False because bitwarden doesn't escape unicode characters
        json.dump(vault_json, newvaultfile, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    dedup(VAULT_WITH_DUPS_PATH, VAULT_DEDUPED_OUTPUT_PATH)

