/* SPDX-License-Identifier: GPL-2.0 */
#ifndef KCAN_COMPAT_STRING_H
#define KCAN_COMPAT_STRING_H

#ifdef __KERNEL__
#include <linux/string.h>
#else
#include <string.h>
#endif

/*
 * Linux 7.3 no longer exposes strncpy(). Preserve the existing fixed-width
 * field ABI exactly: zero-pad short sources; do not append NUL when the
 * source fills count bytes. A strscpy() substitution would change that ABI.
 */
static inline char *kcan_strncpy(char *dest, const char *src, size_t count)
{
    size_t len = strnlen(src, count);

    if (len)
        memcpy(dest, src, len);
    if (len < count)
        memset(dest + len, 0, count - len);
    return dest;
}

#endif /* KCAN_COMPAT_STRING_H */
