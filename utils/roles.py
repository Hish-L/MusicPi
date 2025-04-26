def is_dj(ctx):
    return any(role.name == "DJ" for role in ctx.author.roles)