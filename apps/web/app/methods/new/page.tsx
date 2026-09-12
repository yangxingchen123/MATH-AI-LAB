import { Breadcrumb } from "../../../components/breadcrumb";
import { CreateObjectForm } from "../../../features/create/create-object-form";

export default function NewMethodPage() {
  return (
    <article>
      <Breadcrumb
        items={[
          { href: "/", label: "工作台" },
          { href: "/methods", label: "方法" },
          { label: "新建" },
        ]}
      />
      <CreateObjectForm operation="CreateMethod" heading="创建方法" />
    </article>
  );
}
