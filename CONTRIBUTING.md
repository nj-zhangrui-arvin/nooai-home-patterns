# Contributing

        ## 中文

        - 只使用合成数据、example namespace 和可公开的文档素材。
        - 先用最小测试锁定行为，再做清理、重构或文案调整。
        - 一次提交只解决一个可独立回滚的问题。
        - 不提交运行日志、备份、数据库、`.storage`、私有脚本或媒体原件。

        提交前运行：

        ```bash
        env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
env PYTHONDONTWRITEBYTECODE=1 python3 tools/check_public_export.py .
        ```

        ## English

        - Use only synthetic data, example namespaces, and publicly reviewable documentation assets.
        - Lock behavior with the smallest relevant tests before cleanup, refactor, or wording changes.
        - Keep each commit independently reviewable and revertible.
        - Do not commit runtime logs, backups, databases, `.storage`, private scripts, or original household media.

        Before opening a PR, run:

        ```bash
        env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
env PYTHONDONTWRITEBYTECODE=1 python3 tools/check_public_export.py .
        ```
