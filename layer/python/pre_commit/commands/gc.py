from __future__ import annotations

import os.path
from typing import Any

import pre_commit.constants as C
from pre_commit import output
from pre_commit.clientlib import InvalidConfigError
from pre_commit.clientlib import InvalidManifestError
from pre_commit.clientlib import load_config
from pre_commit.clientlib import load_manifest
from pre_commit.clientlib import LOCAL
from pre_commit.clientlib import META
from pre_commit.store import Store


def _mark_used_repos(
        store: Store,
        all_repos: dict[tuple[str, str], str],
        unused_repos: set[tuple[str, str]],
        repo: dict[str, Any],
) -> None:
    if repo['repo'] == META:
        return
    elif repo['repo'] == LOCAL:
        for hook in repo['hooks']:
            deps = hook.get('additional_dependencies')
            unused_repos.discard((
                store.db_repo_name(repo['repo'], deps), C.LOCAL_REPO_VERSION,
            ))
    else:
        key = (repo['repo'], repo['rev'])
        path = all_repos.get(key)
        # can't inspect manifest if it isn't cloned
        if path is None:
            return

        try:
            manifest = load_manifest(os.path.join(path, C.MANIFEST_FILE))
        except InvalidManifestError:
            return
        else:
            unused_repos.discard(key)
            by_id = {hook['id']: hook for hook in manifest}

        for hook in repo['hooks']:
            if hook['id'] not in by_id:
                continue

            deps = hook.get(
                'additional_dependencies',
                by_id[hook['id']]['additional_dependencies'],
            )
            unused_repos.discard((
                store.db_repo_name(repo['repo'], deps), repo['rev'],
            ))


def _gc_repos(store: Store) -> int:
    configs = store.select_all_configs()
    repos = store.select_all_repos()

    # delete config paths which do not exist
    dead_configs = [p for p in configs if not os.path.exists(p)]
    live_configs = [p for p in configs if os.path.exists(p)]

    all_repos = {(repo, ref): path for repo, ref, path in repos}
    unused_repos = set(all_repos)
    for config_path in live_configs:
        try:
            config = load_config(config_path)
        except InvalidConfigError:
            dead_configs.append(config_path)
            continue
        else:
            for repo in config['repos']:
                _mark_used_repos(store, all_repos, unused_repos, repo)

    store.delete_configs(dead_configs)
    for db_repo_name, ref in unused_repos:
        store.delete_repo(db_repo_name, ref, all_repos[(db_repo_name, ref)])
    return len(unused_repos)


def gc(store: Store) -> int:
    with store.exclusive_lock():
        repos_removed = _gc_repos(store)
    output.write_line(f'{repos_removed} repo(s) removed.')
    return 0
